from rest_framework import serializers
from .models import Movie

# 필터링된 영화 리스트 반환
class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'poster_path',)