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
    <!-- 별점 분포 그래프 -->
    <div class="rating-graph-container">
      <p class="rating-graph-text">별점 그래프</p>
      <canvas id="ratingChart"></canvas>
    </div>
    </div>
  <div
    class="movie-detail-content d-flex flex-column justify-content-center"
  >
    <!-- 영화 추천 -->
    <div class="like-container" @click="likeMovie">
      <div class="like-heart">
        <span class="like-text">{{ isMovieLiked ? '💗' : '🖤' }}</span>
      </div>
      <div class="like-message">
        총 <span class="likes-count">{{ likes_count }}</span>명이 추천했어요!
      </div>
    </div>
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
        <div v-else class="text-center mt-4">
          <h2>리뷰가 없어요! 리뷰를 달아주세용🥺</h2>
        </div>
      </div>
      <!-- 유튜브 -->
      <div>
        <hr />
        <h2>관련 영상</h2>
        <div v-if="movieData && movieData.videos && movieData.videos.length > 2" class="swiper-container" >
          <swiper
            :slides-per-view="2"
            :space-between="40"
            :scrollbar="{ draggable: true }"
            class="thumbnail-swiper"
          >
            <swiper-slide
            v-for="(video, index) in movieData.videos"
              :key="video.id"
              class="thumbnail"
              @click="openModal(video.key)"
            >
              <img
                class="thumbnail-img"
                :src="`https://img.youtube.com/vi/${video.key}/0.jpg`"
                :alt="`Thumbnail ${index + 1}`"
              />
            </swiper-slide>
          </swiper>


          <MovieRelatedVideo
            v-if="isModalOpen"
            :isOpen="isModalOpen"
            @close="closeModal"
            :activeVideoUrl="activeVideoUrl"
          />
        </div>
        <div v-else-if="movieData && movieData.videos && movieData.videos.length <= 2" class="notmany my-4 d-flex justify-content-center">
          <img v-for="(video, index) in movieData.videos"
              :key="video.id"
              @click="openModal(video.key)"
              class="thumbnail-img2 mx-3" 
              :src="`https://img.youtube.com/vi/${video.key}/0.jpg`" 
              :alt="`Thumbnail ${index + 1}`"/>
          <MovieRelatedVideo
            v-if="isModalOpen"
            :isOpen="isModalOpen"
            @close="closeModal"
            :activeVideoUrl="activeVideoUrl"
          />
        </div>
      </div>
    </div>
    <CustomAlertModal
      v-if="showAlert"
      :message="alertMessage"
      @close="closeAlert"
    />
  </div>
  
</template>

<script setup>
import { defineProps, ref, watch, onMounted, computed } from "vue";
import { useAccountStore } from "@/stores/accounts";
import { useRouter } from "vue-router";
import axios from "axios";
import { Swiper, SwiperSlide } from "swiper/vue";
import Chart from "chart.js/auto";
import "swiper/css"
import "swiper/css/scrollbar"
import "swiper/swiper-bundle.css";

import ReviewCard from "./ReviewCard.vue";
import MovieRelatedVideo from "./MovieRelatedVideo.vue";
import CustomAlertModal from "../CustomAlertModal.vue";
const store = useAccountStore();

const props = defineProps({
  movieData: Object,
});

const movieId = ref("");
const reviewCount = ref(0);
const reviewData = ref([]);
const videosList = ref([]);
const router = useRouter();

const likes_count = ref(0);
const isMovieLiked = ref(false); 
const showAlert = ref(false);
const alertMessage = ref("");

const goToReviewForm = () => {
  router.push({ name: "ReviewCreateView", params: { movie_id: movieId.value } });
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

// 알림 모달 닫기
const closeAlert = () => {
  showAlert.value = false;
};

// 추천 여부 확인 함수
const fetchMovieLikeStatus = async () => {
  if (store.isLogin && movieId.value) {
    try {
      const response = await axios.get(
        `${store.API_URL}/api/v1/user/${movieId.value}/is_liked/`,
        {
          headers: {
            Authorization: `Token ${store.token}`,
          },
        }
      );
      isMovieLiked.value = response.data.is_liked;
    } catch (error) {
      console.error("추천 여부 확인 중 오류:", error);
    }
  }
};

// 추천 토글 
const likeMovie = async () => {
  if (!store.isLogin) {
    alertMessage.value = "로그인한 회원만 추천할 수 있습니다.";
    showAlert.value = true;
    return;
  }

  try {
    const response = await axios.post(
      `${store.API_URL}/api/v1/movies/${movieId.value}/like/`,
      {},
      {
        headers: {
          Authorization: `Token ${store.token}`,
        },
      }
    );
    likes_count.value = response.data.likes_count;
    isMovieLiked.value = !isMovieLiked.value; // 추천 여부 토글
  } catch (error) {
    console.error("추천 처리 중 오류:", error);
  }
};

// props 변화 또는 초기 렌더링 시 데이터 로드
watch(
  () => props.movieData,
  (newMovieData) => {
    if (newMovieData && newMovieData.id) {
      movieId.value = newMovieData.id;
      likes_count.value = newMovieData.likes_count;
      fetchMovieLikeStatus(); // 추천 여부 확인
    }
  },
  { immediate: true } 
);

onMounted(() => {
  if (props.movieData && props.movieData.id) {
    movieId.value = props.movieData.id;
    likes_count.value = props.movieData.likes_count;
    fetchMovieLikeStatus(); // 추천 여부 확인
  }
});

const chart = ref(null);

// 별점 데이터 불러오기 및 그래프 생성
const loadRatingData = async () => {
  try {
    const response = await axios.get(
      `${store.API_URL}/api/v1/movies/${movieId.value}/rating/`
    );
    const data = response.data;

    const ctx = document.getElementById("ratingChart").getContext("2d");
    if (!ctx) {
      console.error("Canvas 요소를 찾을 수 없습니다.");
      return;
    }

    if (chart.value) {
      chart.value.destroy();
    }

    const maxValue = Math.max(...data.counts);
    const maxIndex = data.counts.indexOf(maxValue);
    const maxLabel = data.labels[maxIndex];

    chart.value = new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: "별점 분포",
            data: data.counts,
            backgroundColor: (context) => {
              const index = context.dataIndex;
              return index === maxIndex
                ? "rgba(255, 99, 132, 0.8)"
                : "rgba(255, 159, 64, 0.4)";
            },
            hoverBackgroundColor: "rgba(255, 99, 132, 0.9)",
            borderRadius: 10,
            barThickness: 20,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 2,
        layout: {
          padding: {
            left: 20,   // 좌측 여백
            right: 40,  // 우측 여백
            top: 20,    // 상단 여백
            bottom: 10  // 하단 여백
          }
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (tooltipItem) {
                return `${tooltipItem.raw}명`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              display: false,
            },
            title: {
              display: false,
            }
          },
          y: {
            grid: {
              display: false,
            },
            ticks: {
              display: false,
            },
            title: {
              display: false,
            },
            border: {  // 이 부분을 추가
              display: false
            },
            suggestedMax: maxValue + (maxValue * 0.2),
            suggestedMin: 0
          },
        }
              },
      plugins: [
        {
          id: "customMaxLabel",
          afterDraw: (chart) => {
            const { ctx } = chart;
            const dataset = chart.data.datasets[0];
            const meta = chart.getDatasetMeta(0);
            
            const maxValue = Math.max(...dataset.data);
            const maxIndex = dataset.data.indexOf(maxValue);
            const maxLabel = chart.data.labels[maxIndex];
            
            const bar = meta.data[maxIndex];
            const x = bar.x;
            const y = bar.y;
            
            ctx.save();
            ctx.fillStyle = "rgba(255, 99, 132, 1)";
            ctx.font = "bold 16px Arial";
            ctx.textAlign = "center";
            ctx.textBaseline = "bottom";
            
            ctx.fillText(`${maxLabel}⭐`, x, y - 10);
            ctx.restore();
          }
        }
      ]
    });
  } catch (error) {
    console.error("별점 데이터를 불러오는 중 오류:", error);
  }
};




// movieData 변경 감지 및 데이터 로드
watch(
  () => props.movieData,
  (newMovieData) => {
    if (newMovieData && newMovieData.id) {
      movieId.value = newMovieData.id;
      loadRatingData();
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.movieData && props.movieData.id) {
    movieId.value = props.movieData.id;
    loadRatingData();
  }
});
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
  height: 268px;
  cursor: pointer;

}
.notmany {
  height: 268px;

}
.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: none;
  border-radius: 8px;
}
.thumbnail-img2 {
  height: 100%;
  width: 480px;
  object-fit: none;
  border-radius: 8px;
  cursor: pointer;
}

/* Swiper 컨테이너 기본 설정 */
.swiper-container {
  position: relative;
  width: 83%;
  margin-left: 100px;
  margin-top: 30px;
}

.like-container {
  display: flex;
  align-items: center;
  gap: 15px; /* 하트와 메시지 간격 */
  cursor: pointer;
  user-select: none;
  margin-bottom: 10px;
}

.like-heart {
  position: relative;
  font-size: 3rem; /* 하트 크기 */
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.3s ease;
}

.like-container:hover .like-heart {
  transform: scale(1.1); /* 하트 확대 효과 */
}

.like-text {
  position: absolute;
  top: 50%; /* 하트 중앙에 텍스트 배치 */
  left: 50%;
  transform: translate(-50%, -50%); /* 정확히 가운데 정렬 */
  font-size: 1.5rem; /* 이모지 크기 */
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.7); /* 가독성을 위한 그림자 */
  padding-left: 30px;
}

.like-message {
  font-size: 1rem; /* 메시지 폰트 크기 */
  color: #333; /* 메시지 텍스트 색상 */
  font-weight: 500;
  margin-left: 20px;
}

.likes-count {
  font-weight: bold;
}
/* 스크롤바 스타일 */
/* swiper 기본 스타일과 스크롤바 스타일 추가 */
@import 'swiper/css';
@import 'swiper/css/scrollbar';  /* 스크롤바 스타일 */

.swiper-scrollbar {
  height: 6px;               /* 스크롤바 높이 */
  background: #eb6bcf !important;       /* 스크롤바 배경색 */
  border-radius: 3px;        /* 스크롤바 둥글게 */
  margin-top: 10px;          /* 스크롤바 위치 조정 */
}

.swiper-scrollbar-drag {
  background: #007bff;       /* 스크롤바 드래그 색상 */
  border-radius: 3px;        /* 드래그 핸들 둥글게 */
  width: 20px;
  height: 100%;
}

.swiper-scrollbar-drag.swiper-scrollbar-drag-moving {
  background: #0056b3;       /* 드래그 버튼을 끌 때 색상 변경 */
  transform: scale(1.2);      /* 드래그 버튼 확대 효과 */
}

/* 그래프 텍스트 스타일 */
.rating-graph-text {
  font-size: 1rem; /* 적당한 텍스트 크기 */
  font-weight: normal; /* 기본 폰트 굵기 */
  text-align: center; /* 중앙 정렬 */
  color: #888; /* 회색 텍스트 색상 */
  margin-bottom: 10px; /* 그래프와의 간격 */
}

/* 그래프와 텍스트 컨테이너 */
.rating-graph-container {
  display: flex;
  flex-direction: column;
  align-items: center; /* 가로로 중앙 정렬 */
  justify-content: center; /* 세로로 중앙 정렬 */
  margin-top: 20px; /* 상단 간격 */
  padding: 10px; /* 내부 여백 */
}
</style>