<template>
  <div>
    <!-- 상단 navbar - 이미지까지 -->
    <div class="detail-container">
      <img
        :src="store.getBackDrop(backImg)"
        class="backdrop-img"
        style="
          background-position-x: 50%;
          background-position-y: 50%;
          overflow-x: hidden;
          overflow-x: hidden;
          position: absolute;
          top: 0px;
        "
        alt="backdrop-img"
      />
      <div class="detail-content">
        <div>
          <div class="movie-title">{{ movieTitle }}</div>
          <div class="movie-origin-tit">{{ movieOriginTitle }}</div>
          <div class="movie-det">
            <div>{{ movieRelease }}</div>

            <div class="d-flex flex-row">
              <div class="genres" v-for="genre in movieGenres" :key="genre.id">
                {{ genre.name }}
              </div>
            </div>
            <div class="d-flex flex-row">
              <div
                class="countries"
                v-for="country in movieCountries"
                :key="country.id"
              >
                {{ country.name }}
              </div>
            </div>
          </div>
          <div class="movie-det">상영시간: {{ movieRuntime }}분</div>
        </div>
        <section>
          <div class="possible-ott mb-3">감상 가능 ott</div>
          <ul class="ott-ul">
            <li
              class="ott-li"
              v-for="provider in movieProviders"
              :key="provider.id"
            >
              <img
                class="provider-logo"
                :src="store.getOttPath(provider.logo_path)"
                alt=""
              />
            </li>
          </ul>
        </section>
      </div>
    </div>
    <!-- MovieDetail -->
    <MovieDetailInfo :movieData="movieData" />
  </div>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router";
import MovieDetailInfo from "@/components/Movies/MovieDetailInfo.vue";
import axios from "axios";
import { ref, onMounted } from "vue";
import { useAccountStore } from "../../stores/accounts";

const store = useAccountStore();
const router = useRouter();
const route = useRoute();
const movieId = route.params.movie_id;

// 모든 데이터를 DetailInfo로 넘기기
const movieData = ref([]);

const backImg = ref("");
const movieTitle = ref("");
const movieOriginTitle = ref("");
const movieRelease = ref("");
const movieRuntime = ref("");
const movieCountries = ref([]);
const movieProviders = ref([]);
const movieGenres = ref([]);
console.log(movieId);

onMounted(() => {
  axios({
    method: "get",
    url: `${store.API_URL}/api/v1/movies/${movieId}/`,
  })
    .then((res) => {
      console.log(res.data);
      movieData.value = res.data;
      backImg.value = res.data.backdrop_path;
      movieTitle.value = res.data.title;
      movieOriginTitle.value = res.data.original_title;
      movieRelease.value = res.data.release_date;
      movieRuntime.value = res.data.runtime;
      movieCountries.value = res.data.countries;
      movieProviders.value = res.data.providers;
      movieGenres.value = res.data.genres;
    })
    .catch((err) => {
      console.log(err);
    });
});
</script>

<style scoped>
.detail-container {
  box-sizing: border-box;
  display: block;
  height: 700px;
  position: relative;
}
.backdrop-img {
  background-position: 50%;
  background-repeat: no-repeat;
  background-size: cover;
  justify-content: center;
  width: 100%;
  height: 100%;
  display: flex;
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  /* 백드롭 이미지를 어둡게 만들어 대비 강조 */
  /* width: 100%;
  display: block;
  mix-blend-mode: multiply; 
  filter: brightness(80%); */
}
.detail-content {
  align-items: end;
  bottom: 60px;
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  color: white;
  position: absolute;
  left: 0px;
  right: 0px;
  margin-right: 8vw;
  margin-left: 8vw;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8); /* 검은색 그림자 */
}
.genres {
  margin-right: 10px;
}
.genres:last-child {
  margin-right: 0;
}
.movie-title {
  font-weight: bold;
  font-size: 3rem;
}
.movie-origin-tit {
  font-weight: bold;
  font-size: 2rem;
}
.movie-det {
  font-size: 18px;
}
.provider-logo {
  background-position: 50%;
  background-size: 101%;
  border-radius: 50%;
  width: 85px;
  height: 85px;
  position: relative;
  overflow: hidden;
}
.ott-ul {
  display: flex;
  justify-content: flex-start;
  margin-right: 0;
  padding: 0;
  list-style: none;
}
.ott-li {
  margin-right: 20px;
}
.ott-li:last-child {
  margin-right: 0px;
}
.possible-ott {
  font-size: 18px;
}
</style>
