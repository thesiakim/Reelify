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
    <Pagination
      class="d-flex justify-content-center"
      :current-page="currentPage"
      :total-pages="totalPages"
      :page-group="pageGroup"
      :group-size="groupSize"
      @page-changed="handlePageChange"
    />
  </div>
</template>

<script setup>
import MovieCard from "@/components/Movies/MovieCard.vue";
import Pagination from "@/components/Pagination.vue";
import { useAccountStore } from "@/stores/accounts";
import { ref, computed, watch, onMounted } from "vue";

const store = useAccountStore();
const movies = computed(() => store.searchResults);

// 이후 id, poster_path, title로 접근하여 영화 정보 출력 가능

// 페이지네이션 관련 ====================================
const currentPage = ref(1);
const totalPages = ref(1);
const pageGroup = ref(1);
const groupSize = ref(5);

// 페이지네이션을 적용할 영화 목록
const paginatedMovies = computed(() => {
  const startIndex = (currentPage.value - 1) * groupSize.value;
  const endIndex = startIndex + groupSize.value;
  return movies.value.slice(startIndex, endIndex);
});

// totalPages를 계산하여 업데이트하는 함수
const updateTotalPages = () => {
  totalPages.value = Math.ceil(movies.value.length / 20);
};

// 페이지 변경 시 처리할 함수
const handlePageChange = (page) => {
  currentPage.value = page;
};

// 페이지가 변경될 때마다 페이지 그룹을 갱신
watch(currentPage, () => {
  pageGroup.value = Math.ceil(currentPage.value / groupSize.value);
});

// 컴포넌트가 처음 마운트 될 때 totalPages를 업데이트
onMounted(() => {
  updateTotalPages();
});
</script>

<style scoped>
.movieCardList {
  margin-top: 40px;
}
.search-title {
  margin-bottom: 40px;
}
</style>
