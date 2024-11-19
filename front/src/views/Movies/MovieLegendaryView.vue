<template>
  <div class="top-container">
    <h1>👑명예의 전당👑</h1>
    <div class="topMovie">
      <div class="image-slider">
        <Transition name="fade" mode="out-in">
          <!-- 영화 포스터에 대한 Transition -->
          <img
            v-if="topMovieList.length > 0"
            :src="store.getPosterPath(topMovieList[currentIndex]?.poster_path)"
            :key="currentIndex"
            alt="img"
          />
        </Transition>
        <!-- 영화 제목에 대한 Transition -->
      </div>
    </div>
    <div class="topTitle">
      <Transition name="fade" mode="out-in">
        <p v-if="topMovieList.length > 0" class="tran-text" :key="currentIndex">
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
.top-container {
  text-align: center;
}
.topMovie {
  display: flex;
  flex-direction: row;
  justify-content: center;

  align-items: center;
  margin-top: 10vh;
}

.image-slider {
  position: relative;
  width: 80%;
  max-width: 300px;
  height: 50vh;
  margin: 0 auto;
  overflow: hidden;
}

img {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: 10px;
}
.tran-text {
  margin-top: 20px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  opacity: 0;
  transition: opacity 4s ease;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 2s ease, transform 2s ease;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
.fade-enter-to,
.fade-leave {
  opacity: 1;
  transform: translateX(0);
}
</style>