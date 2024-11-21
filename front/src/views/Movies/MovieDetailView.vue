<template>
  <div>
    <h1>영화 상세 페이지</h1>
    <br /><br />
    <!-- Reelify 로고랑 겹쳐서 클릭이 안 됨..아래로 내리느라 br 태그 사용 css 작업 시 지우면 됨 -->
    <button @click="goToReviewForm">리뷰 작성하기</button>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const goToReviewForm = () => {
  const movieId = route.params.movie_id;
  console.log(movieId);
  router.push({
    name: "ReviewFormView",
  });
};
</script>

<style scoped></style>
