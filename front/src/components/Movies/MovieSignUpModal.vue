<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <h3>어떤 영화를 좋아하세요?</h3>
      <hr>
      <div class="movies-grid">
        <div
          v-for="movie in movies"
          :key="movie.id"
          class="movie-card"
          :class="{ selected: selectedMovies.includes(movie.id) }"
          @click="toggleMovieSelection(movie.id)"
        >
          <img :src="getPosterPath(movie.poster_path)" :alt="movie.title" />
          <p>{{ movie.title }}</p>
        </div>
      </div>
      <button class="btn btn-primary mt-3" @click="confirmSelection">
        선택 완료
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import axios from "axios";
import { useAccountStore } from "@/stores/accounts";

const store = useAccountStore();
const props = defineProps({
  genreIds: {
    type: Array,
    required: true,
  },
  show: {
    type: Boolean,
    required: true,
  },
  alreadySelectedMovies: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["close", "moviesSelected"]);

const movies = ref([]);
const selectedMovies = ref([...props.alreadySelectedMovies]);   // 부모의 상태와 동기화

watch(
  () => props.genreIds,
  async (newGenreIds) => {
    if (newGenreIds.length) {
      try {
        const response = await axios.get(`${store.API_URL}/api/v1/movies/sample/`, {
          params: { genre_ids: newGenreIds.join(",") },
        });
        movies.value = response.data;
      } catch (error) {
        console.error("MovieSignUpModal error", error);
      }
    }
  },
  { immediate: true }
);

const toggleMovieSelection = (movieId) => {
  if (selectedMovies.value.includes(movieId)) {
    // 이미 선택된 경우, 제거
    selectedMovies.value = selectedMovies.value.filter((id) => id !== movieId);
  } else if (selectedMovies.value.length < 10) {
    // 선택된 영화가 10개 미만인 경우 추가
    selectedMovies.value.push(movieId);
  }
  emit("moviesSelected", selectedMovies.value); // 부모에 바로 전달
};

const confirmSelection = () => {
  emit("moviesSelected", selectedMovies.value); // 최종 선택된 영화 전달
  closeModal();
};

const closeModal = () => {
  emit("close");
};

const getPosterPath = (path) => {
  return `https://image.tmdb.org/t/p/w780${path}`;
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  padding: 20px;
  width: 80%;
  max-width: 600px;
  max-height: 80%;
  overflow-y: auto;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}

.movie-card {
  border: 1px solid #ddd;
  border-radius: 10px;
  text-align: center;
  padding: 10px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.movie-card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 10px;
}

.movie-card.selected {
  border: 2px solid #fba1b7; 
  background-color: #fff0f5; 
}
.movie-card:hover {
  transform: scale(1.05);
}
</style>
