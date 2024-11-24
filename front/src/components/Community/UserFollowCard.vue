<template>
  <div class="card d-flex flex-row justify-content-center">
    <img class="profile-img" @click="goToUserPage(follow.username)" :src="follow.profile_img" alt="프로필 이미지">
    <div>{{ follow.username }}</div>
    <div v-if="follow.username != store.userName">
      <button @click="goFollowOrUnFollow(follow.username)" v-if="isFollow != null && isFollow === false">팔로우</button>
      <button @click="goFollowOrUnFollow(follow.username)" v-else-if="isFollow != null && isFollow === true">팔로잉</button>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios';
import { defineProps, onMounted, ref } from 'vue';
import { useAccountStore } from '@/stores/accounts';
import { useRoute, useRouter } from 'vue-router';

const store = useAccountStore()
const router = useRouter()
const props = defineProps({
  follow: Object
})

const isFollow = ref(null)

onMounted(() => {
  axios({
    method: 'get',
    url: `${store.API_URL}/api/v1/user/${props.follow.username}/is_follow/`,
    headers: {
      Authorization: `Token ${store.token}`
    }
  })
    .then((res) => {
      console.log(res)
      isFollow.value = res.data.is_following
      console.log(isFollow.value)
    })
    .catch((err) => {
      console.log(err)
    })
})

// 팔로우 기능 구현
const goFollowOrUnFollow = function (username) {
  axios({
    method: 'post',
    url: `${store.API_URL}/api/v1/user/${props.follow.username}/follow/`,
    headers: {
      Authorization: `Token ${store.token}`
    }
  })
    .then((res) => {
      isFollow.value = res.data.is_following
    })
    
    .catch((err) => {
      console.log(err)
    })
}

// 유저 페이지 이동 함수 
const goToUserPage = function (username) {
  router.push({name: 'UserPageView', params: { username: username }})
}

</script>

<style scoped>
.profile-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #ddd;
  cursor: pointer;
  /* margin-bottom: 10px; */
}
</style>