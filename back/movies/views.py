from django.shortcuts import get_object_or_404, get_list_or_404
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Q
from django.db.models import Count
from django.db.models import Prefetch
from datetime import datetime, timedelta
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework import status

from movies.models import Movie, Country, Genre, Review, Comment
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewListSerializer, ReviewSerializer, CommentListSerializer, CommentSerializer, MyPageSerializer


import re
import random
import requests

User = get_user_model()

'''
회원 가입 시 사용
장르와 popularity를 기준으로 메이저한 영화들을 뽑아서 장르별로 고르게 랜덤 추출한 뒤 반환
'''
@api_view(['GET'])
def sample_movies(request):
    # 관심 장르 ID들
    target_genre_ids = [27, 28, 80, 878, 10749, 10402]
    movies_per_genre = {}  # 장르별 영화 저장

    # 각 장르별 상위 10개 인기 영화 가져오기
    for genre_id in target_genre_ids:
        genre_movies = (
            Movie.objects.filter(genres__id=genre_id)
            .order_by('-popularity')[:10]
        )
        movies_per_genre[genre_id] = list(genre_movies)

    # 중복 방지용 집합과 최종 리스트
    unique_movies = set()
    sampled_movies = []

    # 각 장르에서 최대 3개 샘플링
    for genre_id, movies in movies_per_genre.items():
        genre_sample = random.sample(movies, min(len(movies), 3))
        for movie in genre_sample:
            if movie.id not in unique_movies:
                sampled_movies.append(movie)
                unique_movies.add(movie.id)

    # 부족한 영화 수만큼 추가 샘플링 (최종 20개)
    all_movies = [
        movie for movies in movies_per_genre.values() for movie in movies
        if movie.id not in unique_movies
    ]

    while len(sampled_movies) < 20 and all_movies:
        additional_movie = random.choice(all_movies)
        if additional_movie.id not in unique_movies:
            sampled_movies.append(additional_movie)
            unique_movies.add(additional_movie.id)

    # 정확히 20개로 자르기 (초과될 경우)
    sampled_movies = sampled_movies[:20]

    result = [
        {
            "id": movie.id,
            "title": movie.title,
            "popularity": movie.popularity,
            "poster_path": movie.poster_path,
            "genres": [genre.name for genre in movie.genres.all()],
        }
        for movie in sampled_movies
    ]
    return Response(result, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------------------------------------

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

# 회원 탈퇴
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete(request):
    request.user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)