<template>
  <div class="container mt-4">
    <div v-if="movies.length > 0" class="row movieCardList">
      <h1 class="search-title">이 영화를 찾으시나요?</h1>
      <MovieCard
        v-for="movie in movies"
        class="movieCard col-12 col-sm-6 col-md-4 col-lg-3 mb-4"
        :key="movie.id"
        :movie="movie"
      />
    </div>
    <div
      v-else
      class="d-flex justify-content-center align-items-center"
      style="height: 80vh"
    >
      <h1>영화가 업서여ㅠㅠ😥</h1>
    </div>
  </div>
</template>

<script setup>
import MovieCard from "@/components/Movies/MovieCard.vue";
import { useAccountStore } from "@/stores/accounts";
import { ref, computed } from "vue";

const store = useAccountStore();
const movies = computed(() => store.searchResults);

// 이후 id, poster_path, title로 접근하여 영화 정보 출력 가능
</script>

<style scoped>
.movieCardList {
  margin-top: 40px;
}
.search-title {
  margin-bottom: 40px;
}
</style>
