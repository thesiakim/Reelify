from dj_rest_auth.registration.views import RegisterView
from rest_framework.response import Response
from rest_framework import status
from movies.models import Movie, Review
from accounts.serializers import CustomRegisterSerializer

'''
회원 가입 시 사용자가 선택한 영화를 저장한 뒤 회원 가입 로직을 처리하는 커스텀 함수
'''
class CustomSignUpView(RegisterView):
    serializer_class = CustomRegisterSerializer
    pass
