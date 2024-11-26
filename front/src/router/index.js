import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import SignUpView from "@/views/Accounts/SignUpView.vue";
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
import { useAccountStore } from "@/stores/accounts";
import UserProfileEditView from "@/views/Community/UserProfileEditView.vue";
import ReelBotView from "@/views/Community/ReelBotView.vue";

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
      path: "/movie-list/:page?",
      name: "MovieListView",
      component: MovieListView,
      props: true,
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
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
    },
    {
      path: "/:review_id/review-update",
      name: "ReviewUpdateView",
      component: ReviewFormView,
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
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
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
    },
    {
      path: "/:username/user-review-list",
      name: "UserReviewListView",
      component: UserReviewListView,
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
    },
    {
      path: "/:username/user-follower",
      name: "UserFollowerView",
      component: UserFollowerView,
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
    },
    {
      path: "/:username/user-following",
      name: "UserFollowingView",
      component: UserFollowingView,
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
    },
    {
      path: "/:username/user-like-review",
      name: "UserLikeReviewView",
      component: UserLikeReviewView,
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
    },
    {
      path: "/:username/user-update",
      name: "UserUpdateView",
      component: UserUpdateView,
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
    },
    {
      path: "/:username/profile-img-edit",
      name: "UserProfileEditView",
      component: UserProfileEditView,
      beforeEnter: (to, from, next) => {
        const store = useAccountStore();
        if (!store.isLogin) {
          next({ name: "HomeView" });
        } else {
          next();
        }
      },
    },
    {
      path: "/reelbot",
      name: "ReelBotView",
      component: ReelBotView,
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    return { top: 0 };
  },
});

export default router;
