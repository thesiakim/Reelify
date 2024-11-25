<template>
  <div class="container mt-3s">
    <h1>👑명예의 전당👑</h1>
    <div class="d-flex flex-column justify-content-evenly">
      <div class="poster-section text-center">
        <div class="topMovie">
          <div class="image-slider">
            <Transition name="fade" mode="out-in">
              <!-- 영화 포스터에 대한 Transition -->
              <img
                v-if="topMovieList.length > 0"
                :src="
                  store.getPosterPath(topMovieList[currentIndex]?.poster_path)
                "
                :key="currentIndex"
                alt="img"
              />
            </Transition>
          </div>
          <!-- 영화 제목에 대한 Transition -->
          <div class="topTitle">
            <Transition name="fade" mode="out-in">
              <p
                v-if="topMovieList.length > 0"
                class="tran-text"
                :key="currentIndex"
              >
                <!-- {{ currentIndex + 1 }} -->
                <span v-if="currentIndex === 0">🥇</span>
                <span v-else-if="currentIndex === 1">🥈</span>
                <span v-else-if="currentIndex === 2">🥉</span>
                <span v-else>🏅</span>
                {{ topMovieList[currentIndex]?.original_title }}
              </p>
            </Transition>
          </div>
        </div>
      </div>
      <hr class="my-4" />
      <!-- 순위 목록 섹션 -->
      <div class="rank-section my-4">
        <h2>🏆 어제의 박스오피스 순위 🏆</h2>
        <div class="topMovie topList d-flex align-items-center flex-column">
          <p class="movie-title" v-for="(movie, index) in topMovieList" :key="movie.id">
            {{ index + 1 }}위. {{ movie.original_title }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// import MovieTodayTop from "@/components/Movies/MovieTodayTop.vue";
import axios from "axios";
import { ref, onMounted, watch } from "vue";
import { useAccountStore } from "@/stores/accounts";

const store = useAccountStore();
const topMovieList = ref([]);
const currentIndex = ref(0);

onMounted(() => {
  axios({
    method: "get",
    url: `${store.API_URL}/api/v1/movies/box-office/`,
  })
    .then((res) => {
      topMovieList.value = res.data;
      console.log(res.data);
    })
    .catch((err) => {
      console.log(err);
    });
});
// 데이터가 로드된 후 3초마다 이미지 전환

watch(topMovieList, (newList) => {
  if (newList.length > 0) {
    //데이터가 로드되면, setInterval을 시작
    setInterval(() => {
      currentIndex.value = (currentIndex.value + 1) % newList.length;
    }, 4000);
  }
});
</script>

<style scoped>
.container {
  text-align: center;
}
.topMovie {
  margin-top: 4vh;
}

.image-slider {
  position: relative;
  width: 100%;
  max-width: 300px;
  aspect-ratio: 2 / 3;
  margin: 0 auto;
  overflow: hidden;
  text-align: center;
}

.image-slider img {
  width: 100%;
  height: auto;
  max-width: 100%;
  max-height: 100%;
  display: block;
  border-radius: 10px;
  object-fit: cover;
}
.tran-text {
  margin-top: 20px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  opacity: 0;
  transition: opacity 4s ease;
  word-wrap: break-word;
  word-break: break-word;
  text-align: center;
  max-width: 100%;
}
.movie-title {
  font-size: 20px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 2s ease, transform 2s ease;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
  transform: translateX(50px);
}
.fade-enter-to,
.fade-leave {
  opacity: 1;
  transform: translateX(0);
}
.topList {
  min-width: 200px;
  text-align: left;
  padding: 10px;
  box-sizing: border-box;
}
</style>
