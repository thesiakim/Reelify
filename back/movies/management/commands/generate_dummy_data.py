import random
import os
import json
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.serializers import serialize
from movies.models import Movie, Review, Comment

User = get_user_model()


class Command(BaseCommand):
    help = "더미 데이터 생성"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # 1. 100명의 User 생성
        user_list = []
        for _ in range(100):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='password123'
            )
            user_list.append(user)

        movies = list(Movie.objects.all())
        if len(movies) == 0:
            self.stdout.write(self.style.ERROR("python manage.py loaddata db.json 먼저 해주세요!"))
            return

        # 2. 모든 User가 현재 DB에 저장된 모든 Movie에 대해 각각 10회 추천
        for user in user_list:
            recommended_movies = random.sample(movies, k=10)
            for movie in recommended_movies:
                movie.likes.add(user)

        # 3. 모든 User가 모든 Movie에 대해 10~15개의 리뷰 작성
        for user in user_list:
            reviewed_movies = random.sample(movies, k=random.randint(10, 15))
            for movie in reviewed_movies:
                if not Review.objects.filter(user=user, movie=movie).exists():
                    Review.objects.create(
                        user=user,
                        movie=movie,
                        rating=random.choices(
                            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                            weights=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 특정 수치에 치우치지 않도록 동일 가중치
                            k=1
                        )[0],
                        content=fake.text(max_nb_chars=240) if random.choice([True, False]) else None,
                        is_spoiler=random.choice([True, False]),
                    )

        # 4. 모든 User가 Review에 대해 댓글 또는 대댓글 작성
        reviews = Review.objects.all()
        for user in user_list:
            commented_reviews = random.sample(list(reviews), k=3)
            for review in commented_reviews:
                comment = Comment.objects.create(
                    user=user,
                    review=review,
                    content=fake.text(max_nb_chars=200)
                )
                # 대댓글 작성
                if random.choice([True, False]):
                    reply_user = random.choice(user_list)
                    Comment.objects.create(
                        user=reply_user,
                        review=review,
                        parent_comment=comment,
                        content=fake.text(max_nb_chars=200)
                    )

        # 5. 50명의 User가 각 Review에 대해 추천
        selected_users = random.sample(user_list, k=50)
        for user in selected_users:
            for review in reviews:
                review.likes.add(user)

        # JSON 데이터로 저장
        output_dir = os.path.join('movies', 'fixtures')
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, 'dummy.json')

        # 모든 모델의 데이터를 개별적으로 직렬화
        data = []
        data.extend(json.loads(serialize('json', User.objects.all(), use_natural_primary_keys=True)))
        data.extend(json.loads(serialize('json', Movie.objects.all(), use_natural_primary_keys=True)))
        data.extend(json.loads(serialize('json', Review.objects.all(), use_natural_primary_keys=True)))
        data.extend(json.loads(serialize('json', Comment.objects.all(), use_natural_primary_keys=True)))

        # JSON 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"더미 데이터가 {file_path}에 저장되었습니다."))
