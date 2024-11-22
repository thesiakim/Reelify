<template>
  <div class="card mx-2" style="width: 18rem">
    <img
      :src="store.getPosterPath(movie.poster_path)"
      @click="moveToDetail(movie.id)"
      class="card-img-top"
      alt="movieCardImg"
    />
    <div class="card-body text-center">
      <p class="card-text">
        {{ movie.title }}
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  movie: Object,
});
import { useAccountStore } from "@/stores/accounts";
import { useRouter } from "vue-router";
const store = useAccountStore();
const router = useRouter();

const moveToDetail = function (movieId) {
  router.push({ name: "MovieDetailView", params: { movie_id: movieId } });
};
</script>

<style scoped>
.card-img-top {
  width: 100%;
  height: 80%;
  border-radius: 10px;
}
.card-img-top:hover {
  transform: scale(1.05);
  cursor: pointer;
}
.card {
  border: 0;
  background-color: transparent;
}
.card-text {
  font-size: 20px;
}
</style>