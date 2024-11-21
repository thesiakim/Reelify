<template>
  <div class="review-list-container">
    <!-- 리뷰가 없을 때 -->
    <div v-if="reviews.length === 0" class="no-reviews">
      아직 등록된 리뷰가 없습니다.
    </div>

    <!-- 리뷰가 있을 때 -->
    <div v-else>
      <h2 class="review-list-title">{{ movieTitle }}의 리뷰를 찾으셨나요?</h2>
      <div class="review-card-container">
        <div v-for="review in reviews" :key="review.id">
          <ReviewCard :review="review" />
        </div>
      </div>

      <!-- Pagination 컴포넌트 -->
      <Pagination
        class="d-flex justify-content-center"
        :current-page="currentPage"
        :total-pages="totalPages"
        :page-group="pageGroup"
        :group-size="groupSize"
        @page-changed="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";
import qs from "qs";
import { useAccountStore } from "@/stores/accounts";
import ReviewCard from "@/components/Movies/ReviewCard.vue";
import Pagination from "@/components/Pagination.vue";

// 상태 관리
const currentPage = ref(1);  // 현재 페이지
const totalPages = ref(1);   // 총 페이지 수
const pageGroup = ref(1);    // 현재 페이지 그룹
const groupSize = ref(7);    // 그룹당 페이지 수

const route = useRoute();
const store = useAccountStore();

const movieId = route.params.movie_id;
const API_URL = store.API_URL;
const reviews = ref([]);
const movieTitle = ref("");

// 페이징 처리와 함께 리뷰 데이터 조회
const loadReviews = (page = 1) => {
  axios({
    method: "get",
    url: `${API_URL}/api/v1/movies/${movieId}/reviews/`,
    params: { page },
  })
    .then((response) => {
      reviews.value = response.data.reviews.results;
      movieTitle.value = response.data.movie_title;
      totalPages.value = Math.ceil(response.data.reviews.count / 20); 
      pageGroup.value = Math.ceil(currentPage.value / groupSize.value);
    })
    .catch((error) => {
      console.error(`ReviewListView Error: ${error}`);
    });
};

onMounted(() => {
  loadReviews()
})

// 페이지가 변경될 때마다 페이직 그룹 갱신
watch(currentPage, () => {
  pageGroup.value = Math.ceil(currentPage.value / groupSize.value);
});

// 페이지 변경 핸들러
const handlePageChange = (page) => {
  if (typeof page === "number") {
    currentPage.value = page;
    loadReviews(page);
  }
};
</script>

<style scoped>
.review-list-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 리뷰가 없을 때 메시지 스타일 */
.no-reviews {
  font-size: 24px;
  color: #777;
  text-align: center;
  margin: 50px 0;
}

.review-list-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.review-card-container {
  display: flex;
  flex-direction: column; /* 세로로 정렬 */
  gap: 20px; /* 카드 간격 */
}
</style>
