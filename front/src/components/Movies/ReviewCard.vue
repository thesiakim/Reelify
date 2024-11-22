<template>
  <div class="card review-card">
    <div class="card-body">
      <!-- 왼쪽: 프로필 사진 및 유저 이름 -->
      <div class="user-section">
        <img :src="review.user.profile_img" alt="프로필 이미지" class="user-profile-img" />
        <p class="user-username">{{ review.user.username }}</p>
      </div>

      <!-- 오른쪽: 리뷰 내용 및 상세 정보 -->
      <div class="review-content">
        <div
          class="card-text-wrapper"
          :class="{ blurred: review.is_spoiler && !showContent }"
        >
          <!-- 리뷰 내용 -->
          <p class="card-text">{{ review.content }}</p>

          <!-- 스포일러 경고 메시지 -->
          <div
            v-if="review.is_spoiler && !showContent"
            class="spoiler-warning"
            @click="toggleContent"
          >
            스포일러가 포함된 리뷰입니다. 클릭해서 확인해주세요.
          </div>
        </div>

        <div class="review-stats">
          <p class="review-rating">⭐ {{ review.rating.toFixed(1) }}</p>
          <p class="review-likes" @click="reviewLike">👍 {{ likesCount }}</p>
        </div>
        <div class="review-footer">
          <p class="review-date">🕒 {{ new Date(review.created_at).toLocaleString() }}</p>
          <button class="btn btn-primary review-btn" @click="openReviewDetail">댓글 보기</button>
          <button v-if="store.userName === review.user.username" class="btn btn-primary review-btn" @click="updateReview">수정</button>
          <button v-if="store.userName === review.user.username" class="btn btn-primary review-btn" @click="deleteReview">삭제</button>
        </div>
      </div>
    </div>

    <!-- 리뷰 댓글 모달 -->
    <ReviewDetailModal v-if="showDetailModal" :review-id="reviewId" @close="closeReviewDetail" />

    <!-- 커스텀 알림 모달 -->
    <CustomAlertModal
      v-if="showAlert"
      :message="alertMessage"
      @close="closeAlert"
    />
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import { useAccountStore } from "@/stores/accounts";
import CustomAlertModal from "../CustomAlertModal.vue";
import ReviewDetailModal from "./ReviewDetailModal.vue";
import { useRouter } from "vue-router";

const router = useRouter()
const props = defineProps({
  review: Object, // 리뷰 데이터
});

const store = useAccountStore();
const API_URL = store.API_URL;

const reviewId = props.review.id;
const likesCount = ref(props.review.likes_count || 0);
const showContent = ref(false);
const showDetailModal = ref(false); // 리뷰 상세 모달 상태
const showAlert = ref(false);
const alertMessage = ref("");

// 스포일러 토글 함수
const toggleContent = () => {
  showContent.value = !showContent.value;
};

// 추천 처리 함수
const reviewLike = async () => {
  if (!store.isLogin) {
    alertMessage.value = "로그인한 회원만 추천할 수 있습니다.";
    showAlert.value = true;
    return;
  }

  const token = store.token;

  try {
    const response = await axios.post(
      `${API_URL}/api/v1/reviews/${reviewId}/like/`,
      {},
      {
        headers: {
          Authorization: `Token ${token}`,
        },
      }
    );

    // 추천 성공 시 추천수 업데이트
    likesCount.value = response.data.likes_count;
  } catch (error) {
    if (error.response && error.response.status === 400) {
      // 이미 추천한 경우
      alertMessage.value = error.response.data.message; // "이미 추천한 리뷰입니다."
      showAlert.value = true;
    } else {
      console.error("추천 처리 중 오류 발생:", error);
    }
  }
};

// 리뷰 상세 모달 열기
const openReviewDetail = () => {
  showDetailModal.value = true;
};

// 리뷰 상세 모달 닫기
const closeReviewDetail = () => {
  showDetailModal.value = false;
};

// 알림 모달 닫기
const closeAlert = () => {
  showAlert.value = false;
};

const updateReview = () => {
  router.push({ name: 'ReviewUpdateView', params: { review_id: reviewId}})
}

const deleteReview = () => {
  const token = store.token;
  axios({
    method: 'delete',
    url: `${API_URL}/api/v1/reviews/${reviewId}`,
    headers: {
      Authorization: `Token ${token}`
    }
  })
  .then((response) => {
    console.log('리뷰 삭제 완료')
  })
  .catch((error) => {
    console.log(`리뷰 삭제 중 에러 발생 : ${error}`)
  })
  router.push({ name: 'MovieListView'})
}
</script>


<style scoped>
.review-card {
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 100%;
  display: flex;
  align-items: center;
  padding: 20px;
}

.card-body {
  display: flex;
  gap: 20px;
  width: 100%;
}

.user-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  flex: 0 0 120px;
}

.user-profile-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #ddd;
  margin-bottom: 10px;
}

.user-username {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.review-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-text-wrapper {
  position: relative;
}

.card-text-wrapper.blurred .card-text {
  filter: blur(5px);
  border-radius: 10px;
}

.spoiler-warning {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  color: red;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  cursor: pointer;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.review-stats {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #555;
  margin-bottom: 5px;
}

.review-date {
  font-size: 14px;
  color: #999;
}

.review-btn {
  background-color: #fba1b7;
  border: none;
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 5px;
  transition: background 0.3s ease;
}

.review-btn:hover {
  background-color: #e08fa5;
}

.review-likes {
  cursor: pointer;
  transition: color 0.3s ease;
}

.review-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}
</style>