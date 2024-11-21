<template>
  <div>
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
        <div class="movie-tagline gradient-text">"{{ movieData.tagline }}"</div>
      </div>
    </div>

    <div class="mt-5">
      <hr />
      <h3>출연 / 제작</h3>
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
  </div>
</template>

<script setup>
import { defineProps, ref, watch } from "vue";
import { useAccountStore } from "@/stores/accounts";

const store = useAccountStore();
defineProps({
  movieData: Object,
});
</script>

<style scoped>
.moviePoster {
  width: 20vw;
  height: auto;
  object-fit: cover;
  /* border-radius: 10px; */
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
.movie-actors {
  margin-right: 20px;
}
.text-center {
  text-align: center;
}
</style>
