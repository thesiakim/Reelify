<template>
  <div class="container mt-4">
    <!-- 좋아하는 영화 목록이 있는 경우 -->
    <div class="likemovie-container" v-if="likemovie.length > 0">
      <Swiper
        :slides-per-view="4"
        :space-between="10"
        :breakpoints="breakpoints"
        pagination
      >
        <SwiperSlide v-for="movie in likemovie" :key="movie.id">
          <MovieCard class="movie-card" :movie="movie" />
        </SwiperSlide>
      </Swiper>
    </div>
    <div v-else class="noMovie text-center">
      <h3>아직 추천한 영화가 없어요😱</h3>
      <h5
        v-if="store.userName === route.params.username"
        class="click-btn"
        @click="goToMovieList"
      >
        영화 추천하러 가기!😘
      </h5>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";
import { useAccountStore } from "@/stores/accounts";
import MovieCard from "../Movies/MovieCard.vue";
import { Swiper, SwiperSlide } from "swiper/vue";
import "swiper/swiper-bundle.css"; // Swiper 스타일
import "swiper/css/navigation"; // 네비게이션 스타일
import "swiper/css/pagination"; // 페이지네이션 스타일
import { useRouter, useRoute } from "vue-router";

const store = useAccountStore();
const route = useRoute();
const router = useRouter();

const goToMovieList = function () {
  router.push({ name: "MovieListView" });
};

const props = defineProps({
  likemovie: {
    type: Array,
    required: true,
  },
});
const breakpoints = {
  320: { slidesPerView: 1, spaceBetween: 10 }, // 작은 화면
  768: { slidesPerView: 2, spaceBetween: 15 }, // 태블릿
  1024: { slidesPerView: 4, spaceBetween: 20 }, // 데스크탑
};
</script>

<style scoped>
.likemovie-container {
  margin-top: 30px;
}
.swiper-container {
  width: 100%;
  padding: 10px 0;
}
.movie-card {
  height: 100%;
}
.click-btn {
  cursor: pointer;
  margin-top: 30px;
}
.noMovie {
  margin-top: 30px;
}

/* Swiper 슬라이드 스타일 */
.swiper-slide {
  width: 150px; /* MovieCard 크기와 동일하게 설정 */
  height: 450px; /* MovieCard 크기와 동일하게 설정 */
  display: flex;
  justify-content: center;
  align-items: center;
}

/* MovieCard 이미지 크기 조정 */
.movie-card {
  overflow: hidden;
  border-radius: 10px;
}

/* 반응형 슬라이드 크기 설정 */
@media (max-width: 768px) {
  .movie-card {
    width: 150px;
    height: 225px;
  }
}

@media (max-width: 320px) {
  .movie-card {
    width: 120px;
    height: 180px;
  }
}
</style>
