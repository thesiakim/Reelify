from django.urls import path
from .views import MovieFilteringListView, MovieSearchListView, ReviewListView, ReviewCommentListView
from . import views

urlpatterns = [
    path('movies', MovieFilteringListView.as_view()),                 # 장르별, 국가별 영화 필터링 
    path('movies/sample/', views.sample_movies),                      # 회원가입 시 선택할 샘플 영화 반환
    path('movies/box-office/', views.box_office),                     # 박스 오피스 영화 반환
    path('movies/search/', MovieSearchListView.as_view()),            # 영화 제목에 대해 검색 결과 반환 
    path('movies/<int:movie_pk>/', views.movie_detail),               # 영화 상세 페이지 결과 반환 
    path('movies/<int:movie_pk>/reviews/',ReviewListView.as_view()),  # 특정 영화의 리뷰 목록 반환 
    path('movies/reviews/<int:review_pk>/comments/', ReviewCommentListView.as_view())   # 특정 리뷰의 댓글, 대댓글 반환
] 
