from django.db import models
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

# 장르
class Genre(models.Model):
    id = models.IntegerField(primary_key=True)   # 편의를 위해 API가 제공하는 id값을 PK로 사용
    name = models.CharField(max_length=50)

# 국가
class Country(models.Model):
    name = models.CharField(max_length=10)
    code = models.CharField(max_length=10)

# 배우
class Actor(models.Model):
    id = models.IntegerField(primary_key=True)   # 편의를 위해 API가 제공하는 id값을 PK로 사용
    name = models.CharField(max_length=50)
    popularity = models.FloatField()  
    profile_path = models.TextField()            # 프로필 이미지 주소


# 감독
class Director(models.Model):
    id = models.IntegerField(primary_key=True)   # 편의를 위해 API가 제공하는 id값을 PK로 사용
    name = models.CharField(max_length=50)
    profile_path = models.TextField()            # 프로필 이미지 주소


# 공급사
class Provider(models.Model):
    id = models.IntegerField(primary_key=True)   # 편의를 위해 API가 제공하는 id값을 PK로 사용
    name = models.CharField(max_length=50)
    logo_path = models.CharField(max_length=100)

# 영화
class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)           # 영화 제목
    original_title = models.CharField(max_length=100)  # 원제
    overview = models.TextField()                      # 줄거리
    release_date = models.CharField(max_length=50)     # 개봉일
    popularity = models.FloatField()                   # 인기도
    poster_path = models.TextField()                   # 포스터 이미지 주소
    backdrop_path = models.TextField()                 # 배경 이미지 주소
    runtime = models.TextField()                       # 상영시간
    tagline = models.TextField()                       # 슬로건

    genres = models.ManyToManyField(Genre, related_name='movies')
    actors = models.ManyToManyField(Actor, related_name='movies')
    directors = models.ManyToManyField(Director, related_name='movies')
    providers = models.ManyToManyField(Provider, related_name='movies')
    countries = models.ManyToManyField(Country, related_name='movies')
    likes = models.ManyToManyField(User, related_name='like_movies', blank=True)    # 영화 추천


# 관련 영상 
class Video(models.Model):
    id = models.CharField(primary_key=True, max_length=100)   # 편의를 위해 API가 제공하는 id값을 PK로 사용
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    key = models.CharField(max_length=50)

# 리뷰
class Review(models.Model):
    likes = models.ManyToManyField(User, related_name='like_reviews', blank=True)    # 리뷰 추천
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField()
    content = models.TextField(null=True, blank=True, max_length=250)
    is_spoiler = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # 동일 영화에 중복하여 리뷰 작성 불가능 
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='unique_user_movie_review')
        ]
    
    '''
    추천 알고리즘을 위해 캐시 무효화 조건 설정
    - 새로 리뷰를 작성한 경우, 기존 리뷰를 삭제한 경우, 기존 리뷰 수정 시 rating만 수정한 경우
    '''
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_rating = None

        if not is_new:  
            original = Review.objects.get(pk=self.pk)
            old_rating = original.rating

        super().save(*args, **kwargs)

        if is_new or (old_rating is not None and old_rating != self.rating):
            cache_key = f"user_{self.user.id}_recommendations"
            cache.delete(cache_key)

    def delete(self, *args, **kwargs):
        cache_key = f"user_{self.user.id}_recommendations"
        cache.delete(cache_key)
        super().delete(*args, **kwargs)

        
# 리뷰에 대한 코멘트
class Comment(models.Model):
    likes = models.ManyToManyField(User, related_name='like_comments', blank=True)    # 댓글 추천
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)       