<template>
  <div class="card review-card">
    <div class="card-body">
      <!-- 왼쪽: 프로필 사진 및 유저 이름 -->
      <div class="user-section">
        <img
          @click="goToUserPage(review.user.username)"
          :src="review.user.profile_img"
          alt="프로필 이미지"
          class="user-profile-img"
        />
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
          <p class="review-likes" @click="reviewLike">
            👍 {{ review.likes_count }}
          </p>
        </div>
        <div class="review-footer">
          <p class="review-date">
            🕒 {{ new Date(review.created_at).toLocaleString() }}
          </p>
          <a href="#" class="btn btn-primary review-btn">댓글 보기</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

defineProps({
  review: Object,
});

// 컨텐츠 보이기 상태
const showContent = ref(false);

// 토글 함수
const toggleContent = () => {
  showContent.value = !showContent.value;
};

// 추천, 추천 취소
const reviewLike = () => {
  console.log("리뷰 좋아요 클릭됨!");
  // 좋아요 처리 로직 작성
};

// 유저 페이지 이동 함수
const goToUserPage = function (username) {
  router.push({ name: "UserPageView", params: { username: username } });
};
</script>

<style scoped>
/* 카드 스타일 */
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
  cursor: pointer;
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

/* 블러 처리 및 경고 메시지 */
.card-text-wrapper.blurred .card-text {
  filter: blur(5px); /* 부드러운 블러 효과 */
  border-radius: 10px; /* 끝을 둥글게 */
}

/* 스포일러 경고 메시지 */
.spoiler-warning {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(
    255,
    255,
    255,
    0.6
  ); /* 밝은 회색과 흰색 사이의 반투명 효과 */
  border-radius: 10px; /* 둥근 모서리 */
  color: red; /* 텍스트를 빨간색으로 설정 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  cursor: pointer;
}

/* 리뷰 하단 섹션 */
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
</style>
