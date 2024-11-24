<template>
  <div v-if="review && review.user" class="card">
    <div class="card-body">
      <div class="card-title">
        <div class="d-flex flex-row align-items-center">
          <img class="review-profile" :src="review.user.profile_img" alt="프로필 이미지">
          <div class="d-flex flex-column align-items-center">
            <h5 class="mx-4">{{ review.user.username }}</h5>
            <div>👍{{ review.likes_count }}</div>
          </div>
          <!-- <div class="review-content">{{ review.content }}</div> -->
        </div>
        <hr>
         
        </div>
      <p class="card-text">{{ comment.content }}</p>
      <!-- <div class="d-flex justify-content-end">
        <button class="update-btn mx-2">수정</button>
        <button class="delete-btn">삭제</button>
      </div> -->
    </div>
  </div>
</template>

<script setup>
import axios from 'axios';
import { defineProps, onMounted, ref } from 'vue';
import { useAccountStore } from '@/stores/accounts';


const store = useAccountStore()
const props = defineProps({
  comment: Object
})
const review = ref({})
// 댓글이 달린 리뷰 조회 요청
onMounted(() => {
  
  axios({
    method: 'get',
    url: `${store.API_URL}/api/v1/movies/reviews/${props.comment.review_id}/comments/`
  })
    .then((res) => {
      console.log(res.data.results)
      review.value = res.data.results[0]
    })
    .catch((err) => {
      console.log(err)
    })
})


</script>

<style scoped>
.card {
  width: 400px;
}
.update-btn {
  color: white;
  background-color: #fba1b7;
  border-color: transparent;
  border-radius: 8px;
}
.delete-btn {
  color: white;
  background-color: #fba1b7;
  border-color: transparent;
  border-radius: 8px;
}
.review-profile {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 1px solid #ddd
}
.review-content {
  margin-right: 30px ;
  margin-left: 30px;
}

</style>