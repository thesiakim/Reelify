import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from movies.models import Movie, Review, Comment

User = get_user_model()

'''
Faker를 사용하여 더미 데이터 생성 
python manage.py generate_dummy_data
'''
class Command(BaseCommand):
    help = "리뷰, 리뷰 추천, 영화 추천, 댓글 더미 데이터 생성 코드"

    def handle(self, *args, **kwargs):
        fake = Faker()

        user_list = []
        for _ in range(100):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password='password123'
            )
            user_list.append(user)

        movies = list(Movie.objects.all())
        if len(movies) < 30:
            self.stdout.write(self.style.ERROR("python manage.py loaddata db.json 먼저 해주세요!"))
            return

        for user in user_list:
            selected_movies = random.sample(movies, k=10)
            for movie in selected_movies:
                Review.objects.get_or_create(
                    user=user,
                    movie=movie,
                    defaults={
                        'rating': 0.5,
                        'content': None,
                        'is_spoiler': False,
                    }
                )

        for user in user_list:
            recommended_movies = random.sample(movies, k=30)
            for movie in recommended_movies:
                movie.likes.add(user)  

        for user in user_list:
            reviewed_movies = random.sample(movies, k=5)
            for movie in reviewed_movies:
                if not Review.objects.filter(user=user, movie=movie).exists():
                    Review.objects.create(
                        user=user,
                        movie=movie,
                        rating=random.uniform(1.0, 5.0),  
                        content=fake.text(max_nb_chars=300),  
                        is_spoiler=random.choice([True, False]),
                    )

        reviews = Review.objects.all()
        for _ in range(200):  
            user = random.choice(user_list)
            review = random.choice(reviews)
            comment = Comment.objects.create(
                user=user,
                review=review,
                content=fake.text(max_nb_chars=200)  
            )

            for _ in range(random.randint(0, 2)):
                reply_user = random.choice(user_list)
                Comment.objects.create(
                    user=reply_user,
                    review=review,
                    parent_comment=comment,  
                    content=fake.text(max_nb_chars=200)  
                )

        for review in reviews:
            liked_users = random.sample(user_list, k=random.randint(1, 20))  
            for user in liked_users:
                review.likes.add(user) 

        self.stdout.write(self.style.SUCCESS("더미 데이터 생성 완료!"))