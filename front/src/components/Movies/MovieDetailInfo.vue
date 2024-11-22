<template>
  <div class="container">
    <div class="detail-intro">
      <div class="d-flex flex-row">
        <div class="movie-detail-img">
          <img
            class="moviePoster"
            :src="store.getPosterPath(movieData.poster_path)"
            alt="moviePoster"
          />
        </div>
        <div
          class="movie-detail-content d-flex flex-column justify-content-center"
        >
          <div>{{ movieData.overview }}</div>
          <div class="movie-tagline gradient-text">
            "{{ movieData.tagline }}"
          </div>
        </div>
      </div>
      <!-- 출연진 소개 -->
      <div class="mt-5">
        <hr />
        <h2>출연 / 제작</h2>
        <div class="movie-making">
          <p>감독</p>
          <div class="d-flex flex-wrap justify-content-start">
            <div
              class="col-12 col-md-6 col-lg-3 d-flex flex-column justify-content-center align-items-center mb-4"
              v-for="director in movieData.directors"
              :key="director.id"
            >
              <img
                :src="store.getPosterPath(director.profile_path)"
                alt="directorImg"
              />
              <span>
                {{ director.name }}
              </span>
            </div>
          </div>
          <p>배우</p>
          <div class="d-flex flex-wrap justify-content-start">
            <div
              class="movie-actors col-12 col-md-6 col-lg-3 d-flex flex-column justify-content-center align-items-center mb-4"
              v-for="actor in movieData.actors"
              :key="actor.id"
            >
              <img
                :src="store.getPosterPath(actor.profile_path)"
                alt="actorImg"
                class="actor-img"
              />
              <span class="actor-name">
                {{ actor.name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 리뷰 -->
      <div>
        <hr />
        <div class="review-top d-flex flex-row mb-4">
          <h2>리뷰</h2>
          <button class="create-btn" @click="goToReviewForm">
            리뷰 작성하기
          </button>
        </div>
        <div class="average-rating text-center">
          <h4>🏆{{ movieData.average_rating }}</h4>
        </div>
        <div v-if="movieData.top_reviews && movieData.top_reviews.length > 0">
          <div
            class="d-flex justify-content-end"
            v-if="movieData.has_more_reviews"
          >
            <button class="mb-4" @click="goToReviewList">전체 리뷰 보기</button>
          </div>
          <div class="review-container">
            <ReviewCard
              class="mb-5"
              v-for="review in movieData.top_reviews"
              :key="review.id"
              :review="review"
            />
          </div>
        </div>
        <div v-else class="text-center">
          <h1>리뷰가 없어요! 리뷰를 달아주세용🥺</h1>
        </div>
      </div>
      <!-- 유튜브 -->
      <div>
        <hr />
        <h2>관련 영상</h2>
        <div class="swiper-container">
          <div class="custom-prev" @click="goToPrevSlide">◀</div>
          <div class="custom-next" @click="goToNextSlide">▶</div>
          <swiper
            :slides-per-view="3"
            space-between="10"
            :navigation="{
              nextEl: `.custom-prev`,
              prevEl: `.custom-next`,
            }"
            class="thumbnail-swiper"
          >
            <swiper-slide
              v-for="(video, index) in movieData.videos"
              :key="video.id"
              class="thumbnail"
              @click="openModal(video.key)"
            >
              <img
                :src="`https://img.youtube.com/vi/${video.key}/0.jpg`"
                :alt="`Thumbnail ${index + 1}`"
              />
            </swiper-slide>
          </swiper>
          <!-- </div> -->

          <MovieRelatedVideo
            v-if="isModalOpen"
            :isOpen="isModalOpen"
            @close="closeModal"
            :activeVideoUrl="activeVideoUrl"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, ref, watch, onMounted, computed } from "vue";
import { useAccountStore } from "@/stores/accounts";
import { useRouter } from "vue-router";
import axios from "axios";
import { Swiper, SwiperSlide } from "swiper/vue";
import { Navigation } from "swiper/modules";
import "swiper/swiper-bundle.css";

import ReviewCard from "./ReviewCard.vue";
import MovieRelatedVideo from "./MovieRelatedVideo.vue";
const store = useAccountStore();

const props = defineProps({
  movieData: Object,
});

const movieId = ref("");
const reviewCount = ref(0);
const reviewData = ref([]);
const videosList = ref([]);
const router = useRouter();

const goToReviewForm = () => {
  router.push({
    name: "ReviewCreateView",
    params: { movie_id: movieId.value },
  });
};

const goToReviewList = () => {
  router.push({ name: "ReviewListView", params: { movieId: movieId.value } });
};

watch(
  () => props.movieData,
  (newVal) => {
    if (newVal && newVal.id) {
      movieId.value = newVal.id;
      console.log(movieId.value);
      videosList.value = props.movieData.videos;
    }
  }
);
const swiperRef = ref(null);
// 슬라이드 이동 함수
const goToNextSlide = () => {
  if (swiperRef.value) {
    swiperRef.value.swiper.slideNext();
  }
};
const goToPrevSlide = () => {
  if (swiperRef.value) {
    swiperRef.value.swiper.slidePrev();
  }
};

onMounted(() => {
  // Ensure the swiper is initialized after the DOM is rendered
  if (swiperRef.value) {
    swiperRef.value.swiper.params.navigation = {
      nextEl: ".custom-next",
      prevEl: ".custom-prev",
    };
    swiperRef.value.swiper.update();
  }
});

const isModalOpen = ref(false);
const activeVideoUrl = ref("");

const openModal = (key) => {
  activeVideoUrl.value = `https://www.youtube.com/embed/${key}?autoplay=1&vq=hd1080`;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  activeVideoUrl.value = "";
};
</script>

<style scoped>
.moviePoster {
  width: 20vw;
  height: auto;
  object-fit: cover;
  /* border-radius: 10px; */
}
.detail-intro {
  margin-top: 50px;
  margin-right: 70px;
  margin-left: 70px;
  margin-bottom: 50px;
}
@font-face {
  font-family: "KOTRA_SONGEULSSI";
  src: url("https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_20-10-21@1.0/KOTRA_SONGEULSSI.woff")
    format("woff");
  font-weight: normal;
  font-style: normal;
}
.movie-detail-content {
  /* margin-top: 10px; */
  margin-left: 55px;
  margin-right: 55px;
  font-size: 20px;
}
.movie-tagline {
  font-family: "KOTRA_SONGEULSSI";
  margin-top: 30px;
  text-align: center;
  font-size: 30px;
}

.gradient-text {
  background: linear-gradient(90deg, #ff90bc, #8acdd7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: bold; /* 텍스트 강조 (선택사항) */
  font-size: 1.5rem; /* 텍스트 크기 조정 (선택사항) */
}
.movie-making img {
  background-position: 50%;
  background-size: 101%;
  border-radius: 50%;
  width: 100px;
  height: 100px;
  position: relative;
  overflow: hidden;
}

.text-center {
  text-align: center;
}
@media (max-width: 768px) {
  .d-flex {
    flex-direction: column;
  }
  .movie-detail-img {
    text-align: center;
    margin-bottom: 20px;
  }
  .movie-detail-content {
    margin: 0 auto;
    text-align: center;
    font-size: 16px;
  }
  .movie-tagline {
    font-size: 24px;
  }
  .movie-making img {
    width: 80px;
    height: 80px;
  }
}
.create-btn {
  margin-left: 20px;
}
.review-container {
  margin: 20px 100px;
}
/* .thumbnail-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
} */

.thumbnail {
  width: 300px;
  height: 200px;
  cursor: pointer;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: none;
  border-radius: 8px;
}
/* ::v-deep .swiper-button-next::after,
::v-deep .swiper-button-prev::after {
  content: "";
  font-size: 18px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 10px;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  aspect-ratio: 1/1;
}

::v-deep .swiper-button-next::after {
  content: "▶"; 
}

::v-deep .swiper-button-prev::after {
  content: "◀"; 
} */
.swiper-button-next:hover,
.swiper-button-prev:hover {
  background-color: rgba(0, 0, 0, 0.8);
}
/* Swiper 컨테이너 기본 설정 */
.swiper-container {
  position: relative;
  width: 100%;

  margin-top: 30px;
}

/* 커스텀 네비게이션 버튼 스타일 */
.custom-prev,
.custom-next {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

.custom-prev {
  left: -50px; /* 컨테이너 왼쪽 바깥으로 */
}

.custom-next {
  right: -50px; /* 컨테이너 오른쪽 바깥으로 */
}

.custom-prev:hover,
.custom-next:hover {
  background-color: rgba(0, 0, 0, 0.8);
}
</style>
