from django.urls import path
from .views import MovieFilteringListView, MovieSearchListView, ReviewListView, ReviewCommentListView
from . import views

urlpatterns = [
    path('movies/reviews/<int:review_pk>/comments/', ReviewCommentListView.as_view()),  # 특정 리뷰의 댓글, 대댓글 반환
    path('movies/<int:movie_pk>/like/', views.movie_like_toggle),                       # 특정 영화 추천, 추천 취소
    path('movies/<int:movie_pk>/create-review/', views.create_review),                  # 특정 영화에 리뷰 작성
    path('movies/<int:movie_pk>/reviews/', ReviewListView.as_view()),                   # 특정 영화의 리뷰 목록 반환
    path('reviews/<int:review_pk>/comments/', views.comment_create),                    # 리뷰에 대한 댓글 작성
    path('reviews/<int:review_pk>/like/', views.review_like_toggle),                    # 특정 리뷰 추천
    path('reviews/<int:review_pk>/detail/', views.review_detail),                       # 특정 리뷰 조회 
    path('comments/<int:comment_pk>/replies/', views.comment_create),                   # 특정 댓글에 대한 대댓글 작성
    path('comments/<int:comment_pk>/', views.comment_delete),                           # 댓글, 대댓글 삭제
    path('reviews/<int:review_pk>/', views.review),                                     # 특정 리뷰 수정/삭제
    path('movies/<int:movie_pk>/', views.movie_detail),                                 # 영화 상세 페이지 결과 반환

    path('movies/sample/', views.sample_movies),                                        # 회원가입 시 선택할 샘플 영화 반환
    path('movies/box-office/', views.box_office),                                       # 박스 오피스 영화 반환
    path('movies/search/', MovieSearchListView.as_view()),                              # 영화 제목에 대해 검색 결과 반환
    path('movies', MovieFilteringListView.as_view()),                                   # 장르별, 국가별 영화 필터링

    path('profile-image/', views.update_profile_image),                                 # 회원 이미지 변경 
    path('user-page/<str:username>/', views.user_page),                                 # 회원 페이지 
    path('user/<str:username>/follow/', views.toggle_follow),                           # 팔로우, 언팔로우
    path('user/<int:movie_pk>/is_liked/', views.is_liked),
]
