<template>
  <div class="review-container">
    <h1 v-if="route.name === 'ReviewCreateView'" class="title">리뷰 작성</h1>
    <h1 v-if="route.name === 'ReviewUpdateView'" class="title">리뷰 수정</h1>
    <form class="review-form" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="rating" class="label"></label>
        <div class="stars">
          <span
            v-for="index in 5"
            :key="index"
            class="star"
            :class="{ filled: index <= Math.ceil(formData.rating) }"
            :style="{ '--fill-percentage': getFillPercentage(index) }"
            @mousemove="updateHover(index, $event)"
            @mouseleave="resetRating()"
            @click="setRating(index)"
          >
            ★
          </span>
        </div>
        <!-- 이모지와 텍스트 순서 변경 -->
        <p class="rating-text">
          <span class="emoji-display">{{ currentEmoji }}</span>
          선택한 별점: {{ formData.rating }}
        </p>
        <span v-if="ratingError" class="error-message">별점을 입력해주세요</span>
      </div>

      <div class="form-group">
        <label for="content" class="label">리뷰 내용</label>
        <textarea
          id="content"
          v-model.trim="formData.content"
          placeholder="리뷰를 입력해주세요"
          class="textarea"
        ></textarea>
        <!-- 250자 초과 시 에러 메시지 출력 -->
        <span v-if="formData.content.length > 250" class="error-message">
          내용은 250자 이하여야 합니다.
        </span>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="formData.is_spoiler" />
          스포일러 포함
        </label>
      </div>

      <button
        type="submit"
        class="submit-btn"
        :disabled="formData.content.length > 250"
      >
        완료
      </button>
    </form>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="error">
      <p>{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import axios from "axios";
import { useRouter, useRoute } from "vue-router";
import { useAccountStore } from "@/stores/accounts";

const router = useRouter();
const route = useRoute();
const store = useAccountStore();

const movieIdCreate = ref(null)
const movieIdUpdate = ref(null)

const token = store.token;
const API_URL = store.API_URL;

const formData = ref({
  rating: 0,
  content: "",
  is_spoiler: false,
});

const errorMessage = ref("");

// 별점에 따른 이모지 계산
const currentEmoji = computed(() => {
  const rating = formData.value.rating;
  if (rating <= 1) return "😡";
  if (rating <= 2) return "🫤";
  if (rating <= 3) return "🤔";
  if (rating <= 4) return "🤭";
  return "🥰";
});

// 별점 미리보기 업데이트
const updateHover = (index, event) => {
  const { offsetX, target } = event;
  const starWidth = target.offsetWidth;
  const isHalf = offsetX < starWidth / 2;
  formData.value.rating = isHalf ? index - 0.5 : index;
};

// 별점 리셋
const resetRating = () => {
  formData.value.rating = Math.round(formData.value.rating * 2) / 2;
};

// 별점 고정
const setRating = (index) => {
  formData.value.rating = index;
};

// 별 채우기 비율 계산
const getFillPercentage = (index) => {
  if (formData.value.rating >= index) return "100%";
  if (formData.value.rating + 0.5 === index) return "50%";
  return "0%";
};

const ratingError = ref(false);

const handleSubmit = async () => {
  // 리뷰 길이 초과 시 요청 차단
  if ((formData.content || "").length > 250) {
      errorMessage.value = "내용은 250자 이하여야 합니다.";
      return;
    }

  // 별점 미입력 시 요청 차단
  if (formData.value.rating === 0) {
    ratingError.value = true;
    return;
  }
  ratingError.value = false;

  if (route.name === "ReviewCreateView") {
    await createReview();
  } else {
    await updateReview();
  }
};

const createReview = async () => {
  movieIdCreate.value = route.params.movie_id
  try {
    const response = await axios.post(
      `${API_URL}/api/v1/movies/${movieIdCreate.value}/create-review/`,
      formData.value,
      {
        headers: {
          Authorization: `Token ${token}`,
        },
      }
    );
    console.log("리뷰 작성 성공:", response.data);
    router.push({ name: 'MovieDetailView', params: {movie_id: movieIdCreate.value}})
  } catch (error) {
    errorMessage.value = error.response?.data?.message || "리뷰 작성 중 오류가 발생했습니다.";
    console.log()
  }
};

const reviewDetail = ref(null);

const getReviewDetail = function (reviewId) {
  axios
    .get(`${API_URL}/api/v1/reviews/${reviewId}/detail/`)
    .then((response) => {
      reviewDetail.value = response.data;
      console.log(response.data.movie.id)
      movieIdUpdate.value = response.data.movie.id
      console.log(reviewDetail.value)
    })
    .catch(() => {
      console.log("리뷰 수정 시 기존 데이터 불러오는 API 에러 발생");
    });
};

watch(
  () => reviewDetail.value,
  (val) => {
    formData.value.rating = val.rating;
    formData.value.content = val.content;
    formData.value.is_spoiler = val.is_spoiler;
  }
);

if (route.name === "ReviewUpdateView") {
  getReviewDetail(route.params.review_id);
}

const updateReview = function () {
  const reviewId = route.params.review_id;
  axios
    .put(`${API_URL}/api/v1/reviews/${reviewId}/`, formData.value, {
      headers: {
        Authorization: `Token ${token}`,
      },
    })
    .then((response) => {
      console.log("리뷰 수정 성공");
      router.push({ name:'MovieDetailView', params: { movie_id: movieIdUpdate.value }})
    })
    .catch((error) => {
      console.error("리뷰 수정 중 오류:", error);
    });
};
</script>

<style scoped>
/* Container 스타일 */
.review-container {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #f9f9f9;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 제목 스타일 */
.title {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

/* 폼 스타일 */
.review-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.label {
  font-weight: bold;
  margin-bottom: 5px;
  color: #555;
}

.textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  min-height: 100px;
  font-size: 14px;
  resize: none;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #555;
}

.submit-btn {
  padding: 10px 20px;
  background: #fba1b7; /* 여기서 색상을 변경합니다 */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.submit-btn:hover {
  background: #e08fa5; /* 호버 시 약간 더 어두운 색상으로 변경 (선택 사항) */
}

/* 별점 스타일 */
.stars {
  display: flex;
  gap: 5px;
}

.star {
  font-size: 32px;
  color: gray;
  cursor: pointer;
  position: relative;
  transition: color 0.2s ease;
}

.star::before {
  content: "★";
  position: absolute;
  top: 0;
  left: 0;
  width: var(--fill-percentage, 0);
  overflow: hidden;
  color: gold;
}

.rating-text {
  font-size: 12px;
  color: #555;
  margin-bottom: 2px; /* 아래 요소와 간격을 최소화 */
}


/* 에러 메시지 */
.error {
  color: red;
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
}

.error-message {
  color: red;
  font-size: 0.9em;
  margin-top: 5px;
}
.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 수정된 이모지와 텍스트 배치 */
.rating-text {
  font-size: 14px;
  color: #555;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 5px; /* 이모지와 텍스트 간 간격 */
}

.emoji-display {
  font-size: 20px; /* 이모지 크기 */
}
</style>
