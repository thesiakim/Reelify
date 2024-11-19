from django.urls import path
from .views import MovieFilteringListView, MovieSearchListView
from . import views

urlpatterns = [
    path('movies', MovieFilteringListView.as_view()),       # 장르별, 국가별 영화 필터링 
    path('movies/sample/', views.sample_movies),            # 회원가입 시 선택할 샘플 영화 반환
    path('movies/box-office/', views.box_office),           # 박스 오피스 영화 반환
    path('movies/search/', MovieSearchListView.as_view()),  # 영화 제목에 대해 검색 결과 반환 
    path('movies/<int:pk>/', views.movie_detail),           # 영화 상세 페이지 결과 반환 
] 
