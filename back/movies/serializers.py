from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Movie, Genre, Country, Review, Director, Actor, Provider, Video, Comment

User = get_user_model()

# 필터링된 영화 리스트 반환
class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'poster_path',)

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        exclude = ('popularity',)

class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = '__all__'

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        exclude = ('name',)

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        exclude = ('movie',)

class ReviewSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    class Meta:
        model = Review
        fields = ('id', 'user', 'content', 'rating', 'likes_count', 'is_spoiler', 'created_at')

# -------------------------------------------------------------------------------------------------------
# 영화 상세 페이지 
class MovieDetailSerializer(serializers.ModelSerializer):
    
    genres = GenreSerializer(read_only=True, many=True)
    actors = ActorSerializer(read_only=True, many=True)
    directors = DirectorSerializer(read_only=True, many=True)
    providers = ProviderSerializer(read_only=True, many=True)
    countries = CountrySerializer(read_only=True, many=True)
    videos = VideoSerializer(source='video_set', many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    top_reviews = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_more_reviews = serializers.SerializerMethodField()  

    class Meta:
        model = Movie
        exclude = ('popularity', 'likes') 
    
    # 해당 영화에 달린 리뷰들의 평균 rating 계산
    def get_average_rating(self, obj):
        avg_rating = obj.review_set.aggregate(average=Avg('rating'))['average']
        return round(avg_rating, 2) if avg_rating is not None else 0.0
    
    # 추천 및 등록일 순으로 상위 5개의 review 가져오기
    # 리뷰가 없는 경우 빈 리스트 [] 반환 
    def get_top_reviews(self, obj):
        top_reviews = obj.review_set.annotate(
            likes_count=Count('likes')
        ).order_by('-likes_count', '-created_at')[:5]
        return ReviewListSerializer(
            top_reviews, many=True, context=self.context  
        ).data
    
    # 해당 영화를 추천한 유저 수 반환
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    # 화면에 리뷰 렌더링 시 더보기 버튼 필요 여부 확인
    def get_has_more_reviews(self, obj):
        review_count = obj.review_set.count()
        return review_count >= 6

# -------------------------------------------------------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    profile_img = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_img')

    def get_profile_img(self, obj):
        request = self.context.get('request')
        if request and obj.profile_img:
            return request.build_absolute_uri(obj.profile_img.url)
        return None

# 리뷰 목록 
class ReviewListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, context=None)  
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'user', 'content', 'rating', 'likes_count', 'is_spoiler', 'created_at',)

    def get_likes_count(self, obj):
        return obj.likes.count()

# 단일 리뷰
class ReviewSerializer(serializers.ModelSerializer):
    class MovieIdSerializer(serializers.ModelSerializer):
        class Meta:
            model = Movie
            fields = ('id',)

    movie = MovieIdSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ('rating', 'content', 'is_spoiler', 'movie',)
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'likes',)   


# 리뷰에 대한 댓글, 댓글에 대한 대댓글
class CommentListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()      # 대댓글 
    likes_count = serializers.SerializerMethodField()  # 추천 수 

    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'likes_count', 'created_at', 'replies',)

    def get_replies(self, obj):
        replies = obj.replies.all()  # related_name='replies'로 연결된 대댓글
        return CommentListSerializer(replies, many=True, context=self.context).data

    def get_likes_count(self, obj):
        return obj.likes.count()

#------------------------------------------------------------------------------------------------------------

# 댓글 작성 및 수정
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ('id', 'user', 'review', 'parent_comment', 'content', 'created_at', 'updated_at',)
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'review', 'parent_comment',)

#------------------------------------------------------------------------------------------------------------

# 회원 프로필 사진 변경
class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('profile_img',)

# 마이페이지
class MyPageSerializer(serializers.ModelSerializer):
    profile_img = serializers.ImageField()
    username = serializers.CharField()
    followings_count = serializers.IntegerField(source='followings.count', read_only=True)
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    written_reviews = serializers.SerializerMethodField()
    written_comments = serializers.SerializerMethodField()
    liked_reviews = serializers.SerializerMethodField()
    liked_movies = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'profile_img',
            'username',
            'followings_count',
            'followers_count',
            'written_reviews',
            'written_comments',
            'liked_reviews',
            'liked_movies',
        )

    def get_written_reviews(self, obj):
        reviews = obj.review_set.select_related('movie')   # 성능 최적화 : select_related
        return [
            {
                'id': review.id,
                'content': review.content,
                'movie': {
                    'id': review.movie.id,
                    'title': review.movie.title,
                    'poster_path': review.movie.poster_path
                }
            }
            for review in reviews
        ]

    def get_written_comments(self, obj):
        comments = obj.comment_set.all()
        return [{'id': comment.id, 'content': comment.content, 'review_id': comment.review.id} for comment in comments]

    def get_liked_reviews(self, obj):
        liked_reviews = obj.like_reviews.select_related('movie')  
        return [
            {
                'id': review.id,
                'content': review.content,
                'movie': {
                    'id': review.movie.id,
                    'title': review.movie.title,
                    'poster_path': review.movie.poster_path
                }
            }
            for review in liked_reviews
        ]

    def get_liked_movies(self, obj):
        liked_movies = obj.like_movies.all()
        return [{'id': movie.id, 'title': movie.title, 'poster_path': movie.poster_path} for movie in liked_movies]

#------------------------------------------------------------------------------------------------------------
