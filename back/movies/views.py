from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Avg, Count, Max, Q, Prefetch, FloatField, OuterRef, Subquery, F, ExpressionWrapper, Sum, Value
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from collections import OrderedDict, Counter, defaultdict
from itertools import chain
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status

from movies.models import Movie, Country, Genre, Review, Comment, Actor, Director
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewListSerializer, ReviewSerializer, CommentListSerializer, CommentSerializer, MyPageSerializer, UserSerializer, GenreSerializer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine
from heapq import nlargest
import re, random, requests
import numpy as np

User = get_user_model()

'''
회원 가입 시 사용
사용자가 선택한 장르 중 popularity를 기준으로 30개를 정렬한 뒤 랜덤으로 추출
요청 형식 : /api/v1/movies/sample/?genre_ids=12,14
'''
@api_view(['GET'])
def sample_movies(request):
    genre_ids = request.query_params.get("genre_ids", "")
    genre_ids = [int(genre_id) for genre_id in genre_ids.split(",") if genre_id.isdigit()]
    
    cache_key = f"sample_movies_{'_'.join(map(str, genre_ids))}"
    cached_movies = cache.get(cache_key)
    
    if cached_movies:
        print('회원 가입 : 캐시된 데이터 사용')
        return Response(cached_movies, status=status.HTTP_200_OK)
    
    movies = (
        Movie.objects.filter(genres__id__in=genre_ids)
        .distinct()
        .order_by('-popularity')[:50]
    )
    movies = list(movies.values('id', 'title', 'poster_path'))
    sampled_movies = random.sample(movies, min(len(movies), 16))
    
    cache.set(cache_key, sampled_movies, timeout=3600)  # 1시간 유효
    
    return Response(sampled_movies, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------------------------------------

'''
유사 사용자 기반 협업 필터링 추천 (2)
- 평점과 추천 데이터를 함께 고려하여 사용자 간 유사성을 계산
'''
def calculate_user_similarity(user_reviews, candidate_reviews, user_likes, candidate_likes):

    # 사용자 리뷰 데이터를 영화 ID를 키로 하는 딕셔너리로 정리
    user_ratings = {movie_id: rating for movie_id, rating in user_reviews}    # 현재 사용자가 평가한 영화와 평점 목록
    candidate_ratings = {movie_id: rating for movie_id, rating in candidate_reviews}   # 비교할 사용자가 평가한 영화와 평점 목록

    # 두 사용자들의 공통 리뷰 영화 추출
    common_movies = set(user_ratings.keys()) & set(candidate_ratings.keys())
    if not common_movies:
        return 0  # 공통 영화가 없으면 유사도 0

    # 추천한 영화에 가중치를 부여
    for movie_id in common_movies:
        if movie_id in user_likes:
            user_ratings[movie_id] *= 1.5       # 추천한 영화에 가중치 1.5배
        if movie_id in candidate_likes:
            candidate_ratings[movie_id] *= 1.5  # 추천한 영화에 가중치 1.5배

    # 가중치가 반영된 평점을 사용해 두 사용자의 코사인 유사도 계산
    # 두 사용자가 공통으로 평가한 영화에서 평점이 얼마나 비슷한지 측정
    user_vector = [user_ratings[movie] for movie in common_movies]
    candidate_vector = [candidate_ratings[movie] for movie in common_movies]

    similarity = 1 - cosine(user_vector, candidate_vector)
    return similarity if not np.isnan(similarity) else 0    # 계산된 유사도 반환

'''
유사 사용자 기반 협업 필터링 추천 (1) 
- 유사 사용자 ID 추출 : 평점 및 추천 데이터 기반 
'''
def get_similar_users(user, threshold=0.5):
    # 현재 사용자 리뷰 및 추천 데이터 로드
    user_reviews = list(Review.objects.filter(user=user).values_list('movie_id', 'rating'))
    user_likes = set(user.like_movies.values_list('id', flat=True))

    # 모든 리뷰와 추천 데이터를 단일 쿼리로 로드
    reviews = Review.objects.exclude(user=user).select_related('user')    # 모든 리뷰 데이터를 로드하여 사용자별로 그룹화
    likes = User.objects.exclude(id=user.id).prefetch_related(            # 모든 추천 데이터를 로드하여 사용자별로 그룹화
        Prefetch('like_movies', queryset=Movie.objects.all(), to_attr='prefetched_likes')
    )

    # 모든 리뷰 데이터를 사용자별로 그룹화
    all_reviews = defaultdict(list)
    for review in reviews:
        all_reviews[review.user_id].append((review.movie_id, review.rating))

    # 추천 데이터를 사용자별로 그룹화
    all_likes = {user.id: {movie.id for movie in user.prefetched_likes} for user in likes}

    # 다른 사용자들과의 유사성을 계산
    similar_users = []
    for candidate_user, candidate_reviews in all_reviews.items():
        candidate_likes = all_likes.get(candidate_user, set())
        similarity = calculate_user_similarity(user_reviews, candidate_reviews, user_likes, candidate_likes)
        # 기준값 이상이면 유사한 사용자로 판단
        if similarity >= threshold:
            similar_users.append(candidate_user)

    return similar_users

'''
유사 사용자 기반 협업 필터링 추천
'''
def collaborative_filtering_recommendations(user, exclude_movies=set(), max_recommendations=10):
    # 취향이 비슷한 회원 찾기
    similar_user_ids = get_similar_users(user, threshold=0.5)

    # 해당 회원들이 좋아한 영화를 DB에서 검색
    '''
    좋아한다의 기준
    - 평점의 평균 (avg_rating) -> 평균 평점이 3.5 이상인 영화 중, 평점이 높을 수록 좋아하는 영화로 간주 (우선 순위 1)
    - 영화를 추천한 사람들의 수 (like_count) -> 추천이 많을수록 좋아하는 영화로 간주 (우선 순위 2)
    - 영화 자체의 인기도 (calculated_popularity) -> 추가적인 가중치 부여 (우선 순위 3)
    '''
    recommended_movies = Movie.objects.filter(
        review__user__in=similar_user_ids
    ).exclude(
        id__in=exclude_movies        # 현재 사용자가 이미 본 영화는 추천에서 제외
    ).distinct().prefetch_related(
        'directors', 'genres', 'actors', 'likes'
    ).annotate(
        avg_rating=Avg('review__rating'),
        like_count=Count('likes'),
        calculated_popularity=F('popularity')
    ).filter(
        avg_rating__gte=3.5  # 평균 평점이 3.5 미만인 경우 추천에서 제외 
    ).order_by(
        '-avg_rating', '-like_count', '-calculated_popularity'
    )[:max_recommendations]  # 정렬 기준: 평균 평점(avg_rating) > 좋아요 수(like_count) > 영화 인기도(calculated_popularity)

    # 정렬된 영화 중에서 최대 max_recommendations 개수만 반환
    return recommended_movies


'''
사용자가 좋아할 만한 영화 속성에 기반한 영화 추천
- 사용자가 리뷰한 영화의 특징(장르, 배우, 감독 등)을 분석해 비슷한 영화를 찾아 추천
'''
def content_based_recommendations(user, exclude_movies=set(), max_recommendations=10):

    # 사용자가 리뷰를 남긴 영화 중 평점이 3.5 이상인 영화 조회
    high_rated_movies = Review.objects.filter(user=user, rating__gte=3.5).values_list('movie', flat=True)

    # 사용자가 추천한 영화 조회
    liked_movies = user.like_movies.values_list('id', flat=True)

    # 리뷰한 영화와 추천한 영화 데이터를 합쳐 선호 영화 목록 생성
    preferred_movies = set(high_rated_movies).union(set(liked_movies))

    # 선호 속성(장르, 배우, 감독) 추출
    preferred_genres = Genre.objects.filter(movies__in=preferred_movies).distinct()
    preferred_actors = Actor.objects.filter(movies__in=preferred_movies).distinct()
    preferred_directors = Director.objects.filter(movies__in=preferred_movies).distinct()

    # 사용자의 선호 장르, 배우, 감독과 겹치는 영화 필터링
    recommended_movies = Movie.objects.filter(
        Q(genres__in=preferred_genres) |
        Q(actors__in=preferred_actors) |
        Q(directors__in=preferred_directors)
    ).exclude(
        id__in=exclude_movies        # 현재 사용자가 리뷰를 남겼거나 추천한 영화는 제외
    ).distinct().prefetch_related(
        'directors', 'genres', 'actors', 'likes'
    ).annotate(
        avg_rating=Avg('review__rating'),  # 평균 평점 계산
        like_count=Count('likes'),         # 추천 수 계산
        score=F('popularity')              # 인기도 가져오기  
    ).order_by(
        '-score'             # 정렬 기준: 인기도(score) > 평균 평점(avg_rating) > 추천 수(like_count)
    )[:max_recommendations]  # 최대 max_recommendations 개수만 반환

    return recommended_movies



'''
협업 필터링과 콘텐츠 기반 추천 결과 결합 
'''
def get_combined_recommendations(user, max_recommendations=15):
    cache_key = f"user_{user.id}_recommendations"
    cached_recommendations = cache.get(cache_key)

    if cached_recommendations:
        print('추천 알고리즘 : 캐시된 데이터 사용')
        return cached_recommendations

    # 사용자가 이미 리뷰한 영화 및 추천한 영화 제외
    exclude_movies = set(
        Review.objects.filter(user=user).values_list('movie_id', flat=True)
    ).union(
        user.like_movies.values_list('id', flat=True) 
    )

    # 협업 필터링 추천 : 유사한 사용자들이 좋아한 영화를 기반으로 추천
    collab_recommendations = collaborative_filtering_recommendations(user, exclude_movies, max_recommendations)

    # 콘텐츠 기반 추천 : 사용자가 좋아하는 영화의 장르, 배우, 감독과 비슷한 영화를 기반으로 추천
    content_recommendations = content_based_recommendations(user, exclude_movies, max_recommendations)

    # 중복 제거 및 가중치 적용 후 병합
    collab_weight = 1   # 협업 필터링 가중치
    content_weight = 3  # 콘텐츠 기반 추천 가중치 (가중치를 더 높게 설정)

    weighted_collab_ids = [movie.id for movie in collab_recommendations] * collab_weight
    weighted_content_ids = [movie.id for movie in content_recommendations] * content_weight

    combined_movie_ids = set(weighted_collab_ids + weighted_content_ids)

    # 최종적으로 추천할 영화 목록 조회 
    combined_movies = Movie.objects.filter(
        id__in=combined_movie_ids
    ).annotate(
        avg_rating=Avg('review__rating'),
        like_count=Count('likes'),
        calculated_popularity=F('popularity')
    ).order_by('-calculated_popularity', '-avg_rating', '-like_count')[:max_recommendations]   # 인기도(calculated_popularity) > 평균 평점(avg_rating) > 추천 수(like_count) 순으로 정렬

    # 캐시에 저장 (기본 15분)
    cache.set(cache_key, combined_movies, 60 * 15)

    return combined_movies


'''
추천 알고리즘 API
'''
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_movies(request):
    user = request.user

    # 추천 결과 가져오기
    recommended_movies = get_combined_recommendations(user)

    # 결과 직렬화 및 반환
    serializer = MovieListSerializer(recommended_movies, many=True)
    return Response(serializer.data)

#-------------------------------------------------------------------------------------------------------------

'''
영화 별점 분포도 계산
'''
@api_view(['GET'])
def movie_graph(request, movie_pk):
    try:
        movie = Movie.objects.get(pk=movie_pk)
        reviews = Review.objects.filter(movie=movie)
        
        # 별점 분포 계산 (0.5 단위)
        ratings = [0] * 11  # 0.0 ~ 5.0까지 0.5 단위로
        for review in reviews:
            index = int(review.rating * 2)  # 0.5 단위별로 index 계산
            ratings[index] += 1

        distribution = {
            "labels": [f"{i / 2:.1f}" for i in range(11)], 
            "counts": ratings,
        }
        return Response(distribution, status=status.HTTP_200_OK)
    except Movie.DoesNotExist:
        return Response({"message": "존재하지 않는 영화입니다!"}, status=status.HTTP_404_NOT_FOUND)

#-------------------------------------------------------------------------------------------------------------

'''
영화진흥위원회 API를 활용하여 일일 박스오피스 순위 반환
포스터 url을 얻기 위해 TMDB API와 매치하여 영화 제목에 특수문자가 있는 경우 제거한 뒤 개봉일과 가장 근접한 영화 데이터 필터링
'''
# 유니코드 특수문자를 포함한 모든 특수문자 제거 
def clean_title(title): 
    return re.sub(r'[^\w\s]|Ⅱ', '', title, flags=re.UNICODE)


@api_view(['GET'])
def box_office(request):
    # 캐시 키 생성
    cache_key = 'box_office'
    cache_timeout = 60 * 60 * 8  # 8시간 동안 캐시 유지

    # 캐시에서 데이터 가져오기
    cached_data = cache.get(cache_key)
    if cached_data:
        print('캐시된 데이터')
        return Response(cached_data)  # 캐시된 데이터 반환

    # 캐시에 데이터가 없는 경우 API 호출
    KOFIC_API_KEY = settings.KOFIC_API_KEY
    kofic_url = 'http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json'
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    params = {
        'key': KOFIC_API_KEY,
        'targetDt': yesterday.strftime("%Y%m%d")
    }
    box_office_response = requests.get(kofic_url, params=params).json()

    # 필요한 데이터 추출
    rank_movies = [
        {
            'movieNm': movie.get('movieNm'),
            'openDt': movie.get('openDt')  # openDt 형식은 확인 필요
        }
        for movie in box_office_response['boxOfficeResult'].get('dailyBoxOfficeList', [])
    ]

    # TMDB API에서 박스 오피스 순위권의 영화 조회
    TMDB_ACCESS_TOKEN = settings.TMDB_ACCESS_TOKEN
    tmdb_url = 'https://api.themoviedb.org/3/search/movie'

    headers = {
        'Authorization': f'Bearer {TMDB_ACCESS_TOKEN}',
        'accept': 'application/json'
    }

    results = []

    for movie in rank_movies:
        original_title = movie['movieNm']
        clean_movie_title = clean_title(original_title)
        open_date = movie['openDt']

        if not open_date:
            continue  # open_date가 없는 경우 건너뛰기

        try:
            open_date_dt = datetime.strptime(open_date, "%Y-%m-%d")
        except ValueError:
            open_date_dt = datetime.strptime(open_date, "%Y%m%d")

        params = {
            'query': clean_movie_title,
            'language': 'ko-KR',
        }
        search_movie_response = requests.get(tmdb_url, params=params, headers=headers).json()

        if 'results' in search_movie_response and search_movie_response['results']:
            # release_date가 있는 결과만 필터링하고, 날짜가 가까운 순으로 정렬
            valid_results = [
                res for res in search_movie_response['results']
                if 'release_date' in res and res['release_date']
            ]

            if valid_results:
                sorted_results = sorted(
                    valid_results,
                    key=lambda x: abs((datetime.strptime(x['release_date'], "%Y-%m-%d") - open_date_dt).days)
                )
                best_match = sorted_results[0]
                results.append({
                    'original_title': original_title,
                    'poster_path': best_match.get('poster_path'),
                    'id': best_match.get('id')
                })
            else:
                results.append({
                    'original_title': original_title,
                    'poster_path': None,
                    'id': None
                })
        else:
            results.append({
                'original_title': original_title,
                'poster_path': None,
                'id': None
            })

    # 캐시에 데이터 저장
    cache.set(cache_key, results, cache_timeout)

    return Response(results)


#-------------------------------------------------------------------------------------------------------------


# 영화 추천, 추천 취소
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def movie_like_toggle(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)

    if request.user in movie.likes.all():
        movie.likes.remove(request.user)
        liked = False
    else:
        movie.likes.add(request.user)
        liked = True

    return Response({'liked': liked, 'likes_count': movie.likes.count()}, status=status.HTTP_200_OK)


'''
요청 형식 : 다중 조건 만족 

- 필터링 : genre, country
- 정렬 : sort / recent(기본값), review(리뷰순), like(추천순), popularity(인기순)

http://127.0.0.1:8000/api/v1/movies 
http://127.0.0.1:8000/api/v1/movies?genre=12&country=1
http://127.0.0.1:8000/api/v1/movies?genre=12&country=1&genre=14
http://127.0.0.1:8000/api/v1/movies?country=1&country=3&genre=12&genre=14
http://127.0.0.1:8000/api/v1/movies?country=1&sort=popularity
'''
# 일반, 장르, 국가별 영화 필터링
class MovieFilteringListView(ListAPIView):
    serializer_class = MovieListSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Movie.objects.all()

        # 장르 필터링
        genre_ids = self.request.query_params.getlist('genre', None)
        genre_filter = Q()
        if genre_ids:
            try:
                genres = Genre.objects.filter(id__in=genre_ids)
                if not genres.exists():
                    raise NotFound("해당 장르의 영화는 존재하지 않습니다.")
                genre_filter = Q(genres__in=genres)
            except Genre.DoesNotExist:
                raise NotFound("해당 장르의 영화는 존재하지 않습니다.")

        # 국가 필터링
        country_ids = self.request.query_params.getlist('country', None)
        country_filter = Q()
        if country_ids:
            try:
                countries = Country.objects.filter(id__in=country_ids)
                if not countries.exists():
                    raise NotFound("해당 국가의 영화는 존재하지 않습니다.")
                country_filter = Q(countries__in=countries)
            except Country.DoesNotExist:
                raise NotFound("해당 국가의 영화는 존재하지 않습니다.")

        # 국가와 장르의 AND 조건 적용
        if genre_ids and country_ids:
            queryset = queryset.filter(genre_filter & country_filter)
        elif genre_ids:
            queryset = queryset.filter(genre_filter)
        elif country_ids:
            queryset = queryset.filter(country_filter)

        # 정렬 기준 처리
        sort_option = self.request.query_params.get('sort', 'recent')  # 기본값: 최근 개봉일 순

        if sort_option == 'recent':
            queryset = queryset.order_by('-release_date')
        elif sort_option == 'review':
            queryset = queryset.annotate(review_count=Count('review')).order_by('-review_count', '-release_date')
        elif sort_option == 'like':
            queryset = queryset.annotate(like_count=Count('likes')).order_by('-like_count', '-release_date')
        elif sort_option == 'popularity':
            queryset = queryset.order_by('-popularity', '-release_date')
        else:
            raise NotFound("유효하지 않은 정렬 기준입니다.")

        return queryset.distinct()


#-------------------------------------------------------------------------------------------------------------


# 영화 검색 (제목만 허용)
class MovieSearchListView(ListAPIView):
    serializer_class = MovieListSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Movie.objects.all().order_by('-release_date')   # 최근 개봉일 순으로 정렬 

        search_query = self.request.query_params.get('query', None)
        if search_query:
            # title 또는 original_title에 검색어 포함 여부 확인
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(original_title__icontains=search_query)
            )

        return queryset


# 영화 자동 완성 검색
@api_view(['GET'])
def movie_autocomplete(request):
    search_query = request.query_params.get('query', None)
    if not search_query:
        return Response({"detail": "검색어를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    # title 또는 original_title에 검색어 포함 여부 확인
    movies = Movie.objects.filter(
        Q(title__icontains=search_query) |
        Q(original_title__icontains=search_query)
    ).order_by('-release_date')[:10]  # 최대 10개의 결과 반환

    results = movies.values('id', 'title')  # 필요한 필드만 반환
    return Response(results, status=status.HTTP_200_OK)


#-------------------------------------------------------------------------------------------------------------

# @api_view(['GET'])
# def movie_detail(request, pk):
#     # 기존 로직
#     prefetch_reviews = Prefetch(
#         'review_set',
#         queryset=Review.objects.select_related('user').prefetch_related('likes')
#     )
#     movie = Movie.objects.prefetch_related(
#         'genres',
#         'actors',
#         'directors',
#         'providers',
#         'countries',
#         'likes',
#         prefetch_reviews
#     ).get(pk=pk)
    
#     serializer = MovieDetailSerializer(movie)
    
#     # SQL 쿼리 확인
#     for query in connection.queries:
#         print(query)
    
#     return Response(serializer.data)

# 영화 상세 페이지 
'''
쿼리 최적화를 진행한 뒤 Debug Toolbar로 실행 시간을 비교했지만 
대규모 데이터셋 환경이 아니기 때문에 유의미한 차이는 없었음
따라서 기존 코드 유지
'''
@api_view(['GET'])
def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    serializer = MovieDetailSerializer(movie, context={'request': request})
    return Response(serializer.data)


#-------------------------------------------------------------------------------------------------------------


# 특정 영화의 리뷰 목록
'''
- 리뷰가 없는 영화인 경우 빈 배열 [] 반환
- 특정 영화에 대한 리뷰 목록, 각 리뷰에 대한 세부 정보(id, 작성자, 내용, 별점, 스포일러 여부, 추천수, 작성일),
'''
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from .models import Movie, Review
from .serializers import ReviewListSerializer

class ReviewListView(ListAPIView):
    serializer_class = ReviewListSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        movie_id = self.kwargs.get('movie_pk')
        movie = get_object_or_404(Movie, pk=movie_id)
        return Review.objects.filter(movie=movie).order_by('-created_at')

    def get(self, request, *args, **kwargs):
        movie_id = self.kwargs.get('movie_pk')
        movie = get_object_or_404(Movie, pk=movie_id)

        # 리뷰 데이터 가져오기
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                "movie_title": movie.title,
                "reviews": paginated_response.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "movie_title": movie.title,
            "reviews": serializer.data
        })


#-------------------------------------------------------------------------------------------------------------


# 특정 리뷰의 댓글, 대댓글 목록
'''
- 각 리뷰에 달린 댓글의 세부 정보(id, 작성자, 내용, 추천수, 작성일), 
- 각 댓글에 대한 대댓글의 세부 정보(id, 작성자, 내용, 추천수, 작성일)
[
    {
        "id": 101,
        "content": "재밌어요",
        "replies": [
            {"id": 102, "content": "저두요"},
            {"id": 104, "content": "전 별로"}
        ]
    },
    {
        "id": 103,
        "content": "괜찮음",
        "replies": []
    }
]
'''
class ReviewCommentListView(ListAPIView):
    serializer_class = CommentListSerializer
    pagination_class = PageNumberPagination

    # 특정 리뷰에 연결된 최상위 댓글 조회 
    # 직렬화하면서 대댓글 포함
    def get_queryset(self):
        review_id = self.kwargs.get('review_pk')
        return Comment.objects.filter(review_id=review_id, parent_comment__isnull=True).order_by('-created_at')


# -------------------------------------------------------------------------------------------------------------


# 리뷰 작성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, movie_pk):

    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user

    # 중복 리뷰 작성 방지
    if Review.objects.filter(movie=movie, user=user).exists():
        return Response(
            {"message": "이미 리뷰를 작성한 영화입니다."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ReviewListSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user, movie=movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(
            {
                "message": "별점을 지정해주세요!",
                "details": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# 리뷰 수정, 삭제
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def review(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)

    if review.user != request.user:
        return Response(
            {"message": "작성자만 접근할 수 있습니다."},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'PUT':
        serializer = ReviewListSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    "message": "별점을 지정해주세요!",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 단일 리뷰 조회 
@api_view(['GET'])
def review_detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    serializer = ReviewSerializer(review)
    return Response(serializer.data)


# 리뷰 추천
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_like_toggle(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)

    # 이미 추천한 경우
    if request.user in review.likes.all():
        return Response( {"message": "이미 추천한 리뷰입니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 신규 추천
    review.likes.add(request.user)
    return Response(
        {"liked": True, "likes_count": review.likes.count()},
        status=status.HTTP_200_OK
    )
    

# -------------------------------------------------------------------------------------------------------------


# 댓글, 대댓글 작성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, review_pk=None, comment_pk=None):
    # 댓글 작성
    if review_pk:
        try:
            review = Review.objects.get(pk=review_pk)
        except Review.DoesNotExist:
            return Response({"message": "존재하지 않는 리뷰입니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save(user=request.user, review=review)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 대댓글 작성
    elif comment_pk:
        try:
            parent_comment = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            return Response({"message": "존재하지 않는 댓글입니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save(user=request.user, review=parent_comment.review, parent_comment=parent_comment)  # 사용자, 리뷰, 부모 댓글 설정
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)


# 댓글 대댓글 삭제 
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    # 작성자인지 확인
    if comment.user != request.user:
        return Response({"message": "작성자만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# -------------------------------------------------------------------------------------------------------------

# 프로필 이미지 변경
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_image(request):
    user = request.user
    profile_img = request.FILES.get('profile_img')
    
    if not profile_img:
        return Response({'message': '이미지를 지정해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.profile_img = profile_img
    user.save()
    
    return Response(status=status.HTTP_200_OK)


# 유저 페이지 
@api_view(['GET'])
def user_page(request, username):
    user = get_object_or_404(User, username=username)
    serializer = MyPageSerializer(user)
    return Response(serializer.data)


# 팔로우, 언팔로우
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    user = request.user

    if target_user == user:
        return Response({"message": "자기 자신을 팔로우할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    if target_user in user.followings.all():
        user.followings.remove(target_user)
        is_following = False
    else:
        user.followings.add(target_user)
        is_following = True

    return Response({'is_following': is_following, 'followings_count': user.followings.count()})


# 영화 추천 여부 확인 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_liked(request, movie_pk):
    try:
        movie = Movie.objects.get(pk=movie_pk)
        is_liked = movie.likes.filter(pk=request.user.pk).exists()
        return Response({'is_liked': is_liked}, status=status.HTTP_200_OK)
    except Movie.DoesNotExist:
        return Response({"message": "존재하지 않는 영화입니다."}, status=status.HTTP_404_NOT_FOUND)


# 팔로우 여부 확인
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    is_following = request.user.followings.filter(id=target_user.id).exists()
    return Response({ "is_following": is_following })


# 유저 페이지 주인의 팔로우, 팔로잉 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def follow_check(request, username):
    user = get_object_or_404(User, username=username)

    followings = user.followings.all()
    followers = user.followers.all()

    followings_data = UserSerializer(followings, many=True, context={'request': request}).data
    followers_data = UserSerializer(followers, many=True, context={'request': request}).data

    return Response({
        'username': user.username,
        'followings': followings_data,
        'followers': followers_data,
    })


# 유저 페이지 주인의 별점 평균 및 분포도 계산
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def review_graph(request, username):
    user = get_object_or_404(User, username=username)
    user_reviews = Review.objects.filter(user=user)
    
    # 평균 별점 계산
    average_rating = user_reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # 별점 분포 계산
    rating_distribution = (
        user_reviews.values('rating')
        .annotate(count=Count('rating'))
        .order_by('rating')
    )
    distribution_dict = {entry['rating']: entry['count'] for entry in rating_distribution}
    
    return Response({
        "average_rating": round(average_rating, 2),  
        "rating_distribution": distribution_dict,
    })


# 유저 페이지 주인의 선호 장르 계산 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preferred_genres(request, username):
    user = get_object_or_404(User, username=username)

    # User가 작성한 리뷰 중 rating >= 4.0인 리뷰 필터링
    user_reviews = Review.objects.filter(user=user, rating__gte=4.0)

    # 영화와 연결된 장르의 추천 빈도 합산
    genre_preferences = (
        Genre.objects.filter(movies__review__in=user_reviews)
        .annotate(preference_score=Count('movies__likes')) 
        .order_by('-preference_score')
    )

    top_genres = genre_preferences[:3]
    genres_data = [{'id': genre.id, 'name': genre.name} for genre in top_genres]
    serializer = GenreSerializer(genres_data, many=True)

    return Response(serializer.data)



# 회원 탈퇴
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete(request):
    request.user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def send_verification_code(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "이메일을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    
    # 인증번호 생성 및 저장
    verification_code = random.randint(100000, 999999)
    cache.set(email, verification_code, timeout=300)  # 인증번호를 5분간 유효

    # 이메일 발송
    send_mail(
        subject="회원가입 인증번호",
        message=f"안녕하세요, Reelify 입니다. 인증번호 {verification_code}를 입력해주세요!",
        from_email="s20230404@gmail.com",  
        recipient_list=[email],
    )

    return Response({"message": "인증번호가 이메일로 발송되었습니다."}, status=status.HTTP_200_OK)
