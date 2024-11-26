<template>
  <div class="container my-3 text-center">
    <div class="d-flex flex-column">
      <h1>{{ route.params.username }}님의 팔로잉 목록👥</h1>
      <button
        @click="goToUserFollower(route.params.username)"
        class="follow-list-btn ms-md-auto mt-3 mt-md-0"
      >
        팔로워 목록
      </button>
    </div>
    <hr />
    <div v-if="userData.followings && userData.followings.length > 0">
      <UserFollowCard
        class="my-5"
        v-for="following in userData.followings"
        :key="following.id"
        :follow="following"
        @updateFollowStatus="handleFollowStatusUpdate"
        @removeFromList="removeFromList"
      />
    </div>
    <div
      class="my-5"
      v-else-if="userData.followings && userData.followings.length === 0"
    >
      <h2 class="my-4">아직 팔로잉이 없어요😮</h2>
      <h4 class="goTo" @click="goToMovieList">
        누가 어떤 리뷰를 달았는지 봐볼까?🧐
      </h4>
    </div>
  </div>
</template>

<script setup>
import { useAccountStore } from "@/stores/accounts";
import { useRoute, useRouter } from "vue-router";
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import UserFollowCard from "@/components/Community/UserFollowCard.vue";

const store = useAccountStore();
const route = useRoute();
const router = useRouter();

const userData = ref({
  followings: [],
});

onMounted(() => {
  axios({
    method: "get",
    url: `${store.API_URL}/api/v1/user-page/${route.params.username}/follow-check/`,
    headers: {
      Authorization: `Token ${store.token}`,
    },
  })
    .then((res) => {
      console.log(res.data);
      userData.value = res.data;
    })
    .catch((err) => {
      console.log(err);
    });
});

const goToMovieList = function () {
  router.push({ name: "MovieListView" });
};

// 팔로워 목록 이동 함수
const goToUserFollower = function (username) {
  router.push({ name: "UserFollowerView", params: { username: username } });
};
</script>

<style scoped>
.goTo {
  cursor: pointer;
}
.follow-list-btn {
  background-color: #bfecff;
  border: none;
  border-radius: 8px;
  color: white;
  height: 30px;
  width: 100px;
}
</style>
