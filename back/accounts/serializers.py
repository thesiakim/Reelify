from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from movies.models import Movie, Review

# 회원 가입 시 사용할 custom serializer
class CustomRegisterSerializer(RegisterSerializer):
    selectedMovies = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=5,
        max_length=5,
        help_text="사용자가 좋아하는 5개의 영화 ID를 선택해야 합니다."
    )

    def save(self, request):
        # 기본 사용자 생성
        user = super().save(request)

        # 선택된 영화 처리
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
                    {"selectedMovies": f"{movie_id}번 영화는 존재하지 않습니다."}
                )

        return user
