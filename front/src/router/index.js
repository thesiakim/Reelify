import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import SignUpView from "@/views/Accounts/SignUpView.vue";
import AccountUpdateView from "@/views/Accounts/AccountUpdateView.vue";
import MovieListView from "@/views/Movies/MovieListView.vue";
import MovieDetailView from "@/views/Movies/MovieDetailView.vue";
import MovieSearchView from "@/views/Movies/MovieSearchView.vue";
import ReviewListView from "@/views/Movies/ReviewListView.vue";
import ReviewFormView from "@/views/Movies/ReviewFormView.vue";
import MovieMapView from "@/views/Movies/MovieMapView.vue";
import MovieRecommendedView from "@/views/Movies/MovieRecommendedView.vue";
import MovieLegendaryView from "@/views/Movies/MovieLegendaryView.vue";
import UserPageView from "@/views/Community/UserPageView.vue";
import UserReviewListView from "@/views/Community/UserReviewListView.vue";
import UserLikeReviewView from "@/views/Community/UserLikeReviewView.vue";
import UserFollowerView from "@/views/Community/UserFollowerView.vue";
import UserFollowingView from "@/views/Community/UserFollowingView.vue";
import UserUpdateView from "@/views/Accounts/UserUpdateView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "HomeView",
      component: HomeView,
    },
    {
      path: "/sign-up",
      name: "SignUpView",
      component: SignUpView,
    },
    {
      path: "/account-update",
      name: "AccountUpdateView",
      component: AccountUpdateView,
    },
    {
      path: "/movie-list",
      name: "MovieListView",
      component: MovieListView,
    },
    {
      path: "/movie-detail/:movie_id",
      name: "MovieDetailView",
      component: MovieDetailView,
    },
    {
      path: "/movie-search/:movieName",
      name: "MovieSearchView",
      component: MovieSearchView,
    },
    {
      path: "/:movie_id/review-list",
      name: "ReviewListView",
      component: ReviewListView,
    },
    {
      path: "/:movie_id/review-create",
      name: "ReviewCreateView",
      component: ReviewFormView,
    },
    {
      path: "/:review_id/review-update",
      name: "ReviewUpdateView",
      component: ReviewFormView,
    },
    {
      path: "/movie-map",
      name: "MovieMapView",
      component: MovieMapView,
    },
    {
      path: "/movie-recommended",
      name: "MovieRecommendedView",
      component: MovieRecommendedView,
    },
    {
      path: "/movie-legendary",
      name: "MovieLegendaryView",
      component: MovieLegendaryView,
    },
    {
      path: "/user-page/:username",
      name: "UserPageView",
      component: UserPageView,
      props: true,
    },
    {
      path: "/:username/user-review-list",
      name: "UserReviewListView",
      component: UserReviewListView,
    },
    {
      path: "/:username/user-follower",
      name: "UserFollowerView",
      component: UserFollowerView,
    },
    {
      path: "/:username/user-following",
      name: "UserFollowingView",
      component: UserFollowingView,
    },
    {
      path: "/:username/user-like-review",
      name: "UserLikeReviewView",
      component: UserLikeReviewView,
    },
    {
      path: "/:username/user-update",
      name: "UserUpdateView",
      component: UserUpdateView,
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    return { top: 0 };
  },
});

export default router;
