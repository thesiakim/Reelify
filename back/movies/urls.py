from django.urls import path
from .views import MovieFilteringListView, MovieSearchListView, ReviewListView, ReviewCommentListView
from . import views

urlpatterns = [
    path('movies/reviews/<int:review_pk>/comments/', ReviewCommentListView.as_view()),  # 특정 리뷰의 댓글, 대댓글 반환
    path('movies/<int:movie_pk>/rating/', views.movie_graph),                           # 영화 평점 그래프 정보 조회
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
    path('movies/autocomplete/', views.movie_autocomplete),                             # 자동 완성 검색  
    path('movies/<str:person_type>/<int:person_pk>/', views.get_movies_by_person),      # 배우 및 감독의 영화 조회

    path('movies/sample/', views.sample_movies),
    path('movies/box-office/', views.box_office),                                       # 박스 오피스 영화 반환
    path('movies/search/', MovieSearchListView.as_view()),                              # 영화 제목에 대해 검색 결과 반환
    path('movies', MovieFilteringListView.as_view()),                                   # 장르별, 국가별 영화 필터링

    path('recommend/', views.recommend_movies),                                         # 영화 추천 알고리즘

    path('profile-image/', views.update_profile_image),                                 # 회원 이미지 변경 
    path('user-page/<str:username>/preferred_genres/', views.preferred_genres),         # 유저 페이지 주인의 선호 장르 
    path('user-page/<str:username>/follow-check/', views.follow_check),                 # 유저 페이지 주인의 팔로우, 팔로잉 목록 확인
    path('user-page/<str:username>/review-graph/', views.review_graph),                 # 유저 페이지 주인의 평균 별점 및 그래프 
    path('user-page/<str:username>/', views.user_page),                                 # 회원 페이지 
    path('user/<str:username>/follow/', views.toggle_follow),                           # 팔로우, 언팔로우
    path('user/<str:username>/is_follow/', views.is_follow),                            # 유저페이지 주인 팔로우 여부 확인
    path('user/<int:movie_pk>/is_liked/', views.is_liked),                              # 유저의 영화 추천 여부 확인 (화면 렌더링 시 호출하여 동적으로 아이콘 변경)
    
    path('user/delete/', views.delete),                                                 # 회원 탈퇴 
    path('email-verification/', views.send_verification_code),                          # 회원 가입 시 이메일 인증
]