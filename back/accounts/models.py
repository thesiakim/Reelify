from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    profile_img = models.ImageField(upload_to='profile-image/',
                                    default='profile-default.png')

'''
프로필 이미지의 경로는 아래와 같이 프론트에 전달

{
    "username": "yujin",
    "profile_image": "http://127.0.0.1:8000/media/profile_image/yujinprofileimg.jpg"
}
'''