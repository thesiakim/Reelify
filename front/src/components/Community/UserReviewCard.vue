<template>
  <div>
    
      <div class="card " style="width: 25rem;">
        <div class="card-body">
          <div class="d-flex flex-row justify-content-between mb-2">
            <h5 class="card-title">{{ review.movie.title }} </h5>
            <div>🌟{{ review.rating }}</div>
          </div>
          <div class="d-flex flex-row justify-content-center align-items-center">
            <!-- 영화 포스터 -->
            <img @click="goToMovieDetail(review.movie.id)" class="movie-poster-img" :src="store.getPosterPath(review.movie.poster_path)" alt="영화 포스터">
            <!-- 텍스트 및 버튼 -->
            <div class="text-container text-center">
              <p class="card-text">{{ review.content }}</p>
              <div v-if="route.params.username === store.userName" class="text-end">
                <button class="update-btn mx-2" @click="updateReview(review.id)">수정</button>
                <button class="delete-btn" @click="deleteReview(review.id)">삭제</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <hr>
  </div>
</template>

<script setup>
import { useAccountStore } from '@/stores/accounts';
import { useRouter, useRoute } from 'vue-router';
import { onMounted } from 'vue';
import axios from "axios";
const store = useAccountStore()
const router = useRouter()
const route = useRoute()
defineProps({
  review: Object
})

// 영화 디테일로 이동 함수
const goToMovieDetail = function (movieId) {
  console.log(movieId)
  router.push({name:'MovieDetailView', params:{ movie_id: movieId }})
}


// 리뷰 업데이트 함수
const updateReview = function (reviewId) {
  router.push({ name: "ReviewUpdateView", params: { review_id: reviewId}})
}

// 리뷰 삭제 함수
const deleteReview = function (reviewId) {
  const token = store.token

  axios({
    method: 'delete',
    url: `${store.API_URL}/api/v1/reviews/${reviewId}/`,
    headers: {
      Authorization: `Token ${token}`
    }
  })
    .then((res) => {
      console.log('리뷰 삭제 완료')
    })
    .catch((err) => {
      console.log(`리뷰 삭제 중 에러 발생: ${err}`)
    })
    router.push({ name: 'UserPageView', params: { username: `${route.params.username}`}})
}

</script>

<style scoped>
.card {
  border: none;
  max-width: 25rem; /* 적당한 카드 너비 설정 */
  width: 100%;
  background-color: transparent; /* 부모 컨테이너 기준으로 조정 */
}
.movie-poster-img {
  width: 100px;
  height: auto;
  object-fit: cover;
  border-radius: 5px;
  cursor: pointer;
}
.text-container {
  flex: 1; /* 텍스트 영역이 남은 공간을 차지 */
  margin-left: 15px; /* 포스터와 텍스트 사이 간격 */
  overflow: hidden; /* 텍스트 넘침 방지 */
  word-wrap: break-word; /* 긴 단어가 있을 때 줄바꿈 */
}

.card-text {
  white-space: normal;
  word-break: break-word;
  margin-bottom: 10px;
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
</style>
