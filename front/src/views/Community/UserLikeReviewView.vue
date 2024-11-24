<template>
  <div class="container">
    <h1>{{ userData.username }}님이 추천한 리뷰</h1>
    <hr>
    <!-- 추천한 리뷰 -->
    <div class="row review-container d-flex justify-content-center" v-if="userData.liked_reviews && userData.liked_reviews.length > 0" >
      <UserLikeReview class="col-sm-6 mb-3 mb-sm-0 mx-3 my-3" v-for="review in userData.liked_reviews" :key="review.id" :review="review"/>
    </div>

  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useAccountStore } from '@/stores/accounts';
import { useRoute } from 'vue-router';
import UserLikeReview from "@/components/Community/UserLikeReview.vue";

const store = useAccountStore()
const route = useRoute()
const userData = ref([])

onMounted(() => {
  axios({
    method: 'get',
    url: `${store.API_URL}/api/v1/user-page/${route.params.username}/`
  })
    .then((res) => {
      userData.value = res.data
    })
    .catch((err) => {
      console.log(err)
    })
})


</script>

<style scoped>
.review-container {
  margin-top: 20px;
  margin-bottom: 40px;
}
</style>