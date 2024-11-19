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

# 영화 상세 페이지 
class MovieDetailSerializer(serializers.ModelSerializer):
    
    genres = GenreSerializer(read_only=True, many=True)
    actors = ActorSerializer(read_only=True, many=True)
    directors = DirectorSerializer(read_only=True, many=True)
    providers = ProviderSerializer(read_only=True, many=True)
    countries = CountrySerializer(read_only=True, many=True)
    videos = VideoSerializer(source='video_set', many=True, read_only=True)

    class Meta:
        model = Movie
        exclude = ('popularity',)