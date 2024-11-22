<template>
  <div v-if="userData" class="container">
    <h1 class="text-center mt-3">{{ userData.username }}의 영화 취향</h1>
    <div
      class="user-profile d-flex flex-row justify-content-between align-items-center"
    >
      <img
        :src="`${store.API_URL}${userData.profile_img}`"
        class="user-img mx-5"
        alt="profile_img"
      />
      <div class="profile-text text-center">
        <h3>{{ userData.username }}</h3>
        <p class="follow-text">
          팔로우 {{ userData.followers_count }} &ensp;&ensp; 팔로잉{{
            userData.followings_count
          }}
        </p>
      </div>
      <div
        v-if="
          store.isLogin === true &&
          store.userName !== userData.username &&
          isFollow === false
        "
        class="follow-btn"
      >
        <button @click="followUser(userData.username)">팔로우</button>
      </div>
      <div
        v-else-if="
          store.isLogin === true &&
          store.userName !== userData.username &&
          isFollow === true
        "
        class="follow-btn"
      >
        <button @click="unFollowUser(userData.username)">팔로잉</button>
      </div>
      <div
        v-else-if="
          store.isLogin === true && store.userName === userData.username
        "
      >
        <button class="update-btn">내 정보 수정</button>
      </div>
    </div>

    <!-- 영화, 작성 - 추천 리뷰 보여주기 -->
    <div class="">
      <hr />
      <div class="d-flex flex-row justify-content-evenly mt-4">
        <div class="text-center">
          <p>좋아요 한 영화 수</p>
          <span>{{ likeMovieCnt }}</span>
        </div>
        <div class="text-center">
          <p>작성한 리뷰 수</p>
          <span>{{ writeReviewCnt }}</span>
        </div>
        <div class="text-center">
          <p>추천한 리뷰 수</p>
          <span>{{ likeReviewCnt }}</span>
        </div>
      </div>
      <hr />
    </div>

    <!-- 좋아요 한 영화 목록 보여주기 -->
    <div>
      <UserLikeMovie :likemovie="likeMovie" />
    </div>
  </div>
</template>

<script setup>
import { useAccountStore } from "@/stores/accounts";
import { useRoute, useRouter } from "vue-router";
import { onMounted, ref } from "vue";
import axios from "axios";
import UserLikeMovie from "@/components/Community/UserLikeMovie.vue";

const store = useAccountStore();
const route = useRoute();
const router = useRouter();
const userData = ref({});
const likeMovie = ref([]);
const likeMovieCnt = ref(0);
const likeReview = ref([]);
const likeReviewCnt = ref(0);
const writeReview = ref([]);
const writeReviewCnt = ref(0);
console.log(route.params.username);

// 초기에 팔로잉 했는지 안했는지 -> 수정 필요
const isFollow = ref(false);

onMounted(() => {
  axios({
    method: "get",
    url: `${store.API_URL}/api/v1/user-page/${route.params.username}/`,
  })
    .then((res) => {
      console.log(res.data);
      userData.value = res.data;
      likeMovie.value = res.data.liked_movies;
      likeMovieCnt.value = res.data.liked_movies.length;
      likeReview.value = res.data.liked_reviews;
      likeReviewCnt.value = res.data.liked_reviews.length;
      writeReview.value = res.data.written_reviews;
      writeReviewCnt.value = res.data.written_reviews.length;
      console.log(writeReviewCnt.value);
    })
    .catch((err) => {
      console.log(err);
    });
});

const followUser = function (username) {
  axios({
    method: "post",
    url: `${store.API_URL}/api/v1/user/${username}/follow/`,
    headers: {
      Authorization: `Token ${store.token}`,
    },
  })
    .then((res) => {
      isFollow.value = res.data.is_following;
      userData.value.followers_count += 1;
      console.log(isFollow.value);
    })
    .catch((err) => {
      console.log(err);
    });
};
const unFollowUser = function (username) {
  axios({
    method: "post",
    url: `${store.API_URL}/api/v1/user/${username}/follow/`,
    headers: {
      Authorization: `Token ${store.token}`,
    },
  })
    .then((res) => {
      isFollow.value = res.data.is_following;
      userData.value.followers_count -= 1;
      console.log(isFollow.value);
    })
    .catch((err) => {
      console.log(err);
    });
};
</script>

<style scoped>
.user-img {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  border: 5px solid #fba1b7;
}
.user-profile {
  margin-top: 70px;
  margin-bottom: 70px;
  margin-right: 20px;
  margin-left: 20px;
}
.profile-text {
  margin-right: 50px;
  margin-left: 20px;
}
.follow-text {
  font-size: 20px;
}
.update-btn {
  display: flex;
}
@media (max-width: 768px) {
  .profile-text {
    margin-left: 0;
    margin-right: 0;
  }

  .user-img {
    width: 100px;
    height: 100px; /* 화면이 작아지면 이미지 크기도 줄어듬 */
  }

  .follow-text {
    font-size: 1rem;
  }
}

@media (max-width: 576px) {
  .user-profile {
    flex-direction: column !important;
    text-align: center;
  }
  .follow-text {
    font-size: 0.9rem;
  }

  h3 {
    font-size: 1.2rem;
  }

  h1 {
    font-size: 1.5rem;
  }
}
</style>
