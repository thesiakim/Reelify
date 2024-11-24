<template>
  <div class="container my-3 text-center">
    <h1>{{ route.params.username }}님의 팔로워 목록👥</h1>
    <hr>
    <div v-if="userData.followers && userData.followers.length > 0">
      <UserFollowCard class="my-5" v-for="follower in userData.followers" :key="follower.id" :follow="follower"/>
    </div>
    <div class="my-5" v-else-if="userData.followers && userData.followers.length === 0">
      <h2 class="my-4">아직 팔로워가 없어요🥲</h2>
      <h4 class="goTo" @click="goToMovieList">영화에 리뷰 달러 갈까?🎞️</h4>
    </div>
  </div>
</template>

<script setup>
import UserFollowCard from '@/components/Community/UserFollowCard.vue';
import { useAccountStore } from '@/stores/accounts';
import { useRoute, useRouter } from 'vue-router';
import { onMounted, ref } from 'vue';
import axios from 'axios';
const store = useAccountStore()
const route = useRoute()
const router = useRouter()

const userData = ref({})

onMounted(() => {
  axios({
    method: 'get',
    url: `${store.API_URL}/api/v1/user-page/${route.params.username}/follow-check/`,
    headers: {
      Authorization: `Token ${store.token}`
    }
  })
    .then((res) => {
      console.log(res.data)
      userData.value = res.data
    })
    .catch((err) => {
      console.log(err)
    })
})

const goToMovieList = function () {
  router.push({name:"MovieListView"})
}


</script>

<style scoped>
.goTo {
  cursor: pointer;
}
</style>
