from django.db.models import Avg, Count
from rest_framework import serializers
from .models import Movie, Genre, Country, Review, Director, Actor, Provider, Video

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
        return ReviewSerializer(top_reviews, many=True).data
    
    # 해당 영화를 추천한 유저 수 반환
    def get_likes_count(self, obj):
        return obj.likes.count()