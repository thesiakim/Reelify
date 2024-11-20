<template>
  <div class="container">
    <h1>이 영화를 찾으시나요?</h1>
    <!-- <MovieCard v-for="movie in movies" :key="movie.id" :movie="movie" /> -->
  </div>
</template>

<script setup>
import MovieCard from "@/components/Movies/MovieCard.vue";
import { useAccountStore } from "@/stores/accounts";
import { ref } from "vue";

const store = useAccountStore();
const movies = ref(store.searchResults);

// 이후 id, poster_path, title로 접근하여 영화 정보 출력 가능
</script>

<style scoped></style>
