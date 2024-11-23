from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from movies.models import Movie, Review
from django.db import transaction

# 회원 가입 시 사용할 custom serializer
class CustomRegisterSerializer(RegisterSerializer):
    selectedMovies = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="10개의 영화 선택 필수"
    )

    def validate_selectedMovies(self, value):
        # 영화 중복 체크
        if len(value) != len(set(value)):
            raise serializers.ValidationError("선택된 영화 목록에 중복된 영화가 있습니다.")
        
        # 영화 개수 체크
        if len(value) != 10:
            raise serializers.ValidationError("10개의 영화를 선택해야 합니다.")
        
        return value

    def save(self, request):
        user = super().save(request)

        with transaction.atomic():
            selected_movies = self.validated_data.get('selectedMovies', [])
            for movie_id in selected_movies:
                try:
                    movie = Movie.objects.get(id=movie_id)
                    Review.objects.create(
                        user=user,
                        movie=movie,
                        rating=5,
                        content=None,
                        is_spoiler=False,
                    )
                except Movie.DoesNotExist:
                    raise serializers.ValidationError(
                        {"selectedMovies": f"{movie_id}번 영화(ID: {movie_id})는 데이터베이스에 없습니다."}
                    )

        return user

