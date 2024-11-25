<template>
  <div v-if="store.isLogin === true" class="container my-3">
    <h1 class="text-center">🔮Reelify가 {{ store.userName }}님만을 위해 추천하는 영화🔮</h1>
    <div class="row movie-list mt-5 d-flex justify-content-center" v-if="movies">
      <MovieCard v-for="movie in movies" :key="movie.id" :movie="movie" class="movieCard col-12 col-sm-6 col-md-4 col-lg-3 mb-4"/>
    </div>
  </div>
  <div v-else class="container my-3 d-flex flex-column justify-content-center align-items-center vh-100">
    <h1>Reelify가 추천하는 영화를 알고싶나요?</h1>
    <h3>그렇다면 Reelify의 회원이 되어보세요!</h3>
    <h4 class="gradient-text" @click="goToSignUpView">Reelify 회원 되기</h4>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useAccountStore } from '@/stores/accounts';
import { useRouter } from 'vue-router'
import axios from 'axios';
import MovieCard from "@/components/Movies/MovieCard.vue";

const store = useAccountStore()
const router = useRouter()

// 데이터 담을 변수 정의
const movies = ref([])



onMounted(() => {
  if (store.isLogin === true) {
    axios({
    method: 'get',
    url: `${store.API_URL}/api/v1/recommend/`,
    headers: {
      Authorization: `Token ${store.token}`
    }
  })
    .then((res) => {
      console.log(res.data)
      movies.value = res.data
      console.log(movies.value)
    })
    .catch((err) => {
      console.log(err)
    })

  }
  
})

const goToSignUpView = function () {
  router.push({name: 'SignUpView'})
}

</script>

<style scoped>
.gradient-text {
  background: linear-gradient(90deg, #ffccea, #a1eebd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: bold; /* 텍스트 강조 (선택사항) */
  font-size: 1.5rem; /* 텍스트 크기 조정 (선택사항) */
  cursor: pointer;
}

</style>
