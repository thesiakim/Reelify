<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <button class="close-btn" @click="closeModal">x</button>

      <!-- 댓글 입력 -->
      <div class="add-comment">
        <input
          type="text"
          v-model.trim="newComment"
          placeholder="댓글을 입력하세요"
        />
        <button @click="addComment">작성</button>
      </div>

      <div class="comments-container">
        <h4>댓글 목록</h4>
        <div v-if="comments.length > 0">
          <div v-for="comment in comments" :key="comment.id" class="comment">
            <div class="comment-header">
              <img
                :src="comment.user.profile_img"
                alt="프로필 이미지"
                class="profile-img"
              />
              <span class="username">{{ comment.user.username }}</span>
              <span class="created-at">{{ formatDate(comment.created_at) }}</span>
            </div>
            <p class="comment-content">{{ comment.content }}</p>

            <!-- 대댓글 입력 버튼 -->
            <div class="reply-btn">
              <img
                @click="toggleReplyInput(comment.id)"
                src="@/assets/reply-icon.png"
                alt="reply-icon.png"
              />
            </div>

            <!-- 대댓글 입력칸 -->
            <div v-if="showReplyInput === comment.id" class="reply-input">
              <input
                type="text"
                v-model.trim="replyContent"
                placeholder="대댓글을 입력하세요"
              />
              <button @click="addReply(comment.id)">작성</button>
            </div>

            <!-- 대댓글 -->
            <div v-if="Array.isArray(comment.replies) && comment.replies.length > 0" class="replies">
              <div
                v-for="reply in comment.replies"
                :key="reply.id"
                class="reply"
              >
                <div class="comment-header">
                  <img
                    :src="reply.user.profile_img"
                    alt="프로필 이미지"
                    class="profile-img"
                  />
                  <span class="username">{{ reply.user.username }}</span>
                  <span class="created-at">{{ formatDate(reply.created_at) }}</span>
                </div>
                <p class="comment-content">{{ reply.content }}</p>
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <p>댓글이 없습니다.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import { ref, onMounted } from "vue";
import { useAccountStore } from "@/stores/accounts";

const props = defineProps({
  reviewId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["close"]);

const closeModal = () => {
  emit("close");
};

// 댓글 데이터
const comments = ref([]); // 항상 빈 배열로 초기화
const newComment = ref(""); // 새 댓글 내용
const replyContent = ref(""); // 대댓글 내용
const showReplyInput = ref(null); // 대댓글 입력창 상태

const store = useAccountStore();
const API_URL = store.API_URL;
const token = store.token;

// 날짜 포맷 함수
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

// 댓글 목록 가져오기
const loadComments = async () => {
  try {
    const response = await axios.get(
      `${API_URL}/api/v1/movies/reviews/${props.reviewId}/comments/`
    );
    comments.value = response.data.results;
  } catch (error) {
    console.error("댓글 목록을 불러오는 중 오류가 발생했습니다.", error);
  }
};

// 댓글 추가
const addComment = async () => {
  try {
    const response = await axios.post(
      `${API_URL}/api/v1/reviews/${props.reviewId}/comments/`,
      { content: newComment.value },
      { headers: { Authorization: `Token ${token}` } }
    );
    comments.value.unshift(response.data); // 새로운 댓글을 목록의 맨 앞에 추가
    newComment.value = ""; // 입력창 초기화
  } catch (error) {
    console.error("댓글 작성 시 오류:", error);
  }
};

// 대댓글 입력창 토글
const toggleReplyInput = (commentId) => {
  showReplyInput.value = showReplyInput.value === commentId ? null : commentId;
};

// 대댓글 추가
const addReply = async (commentId) => {
  try {
    const response = await axios.post(
      `${API_URL}/api/v1/comments/${commentId}/replies/`,
      { content: replyContent.value },
      { headers: { Authorization: `Token ${token}` } }
    );
    const commentIndex = comments.value.findIndex((c) => c.id === commentId);
    if (commentIndex !== -1) {
      if (!Array.isArray(comments.value[commentIndex].replies)) {
        comments.value[commentIndex].replies = []; // replies를 빈 배열로 초기화
      }
      comments.value[commentIndex].replies.push(response.data); // 대댓글 추가
    }
    replyContent.value = ""; // 대댓글 입력창 초기화
    showReplyInput.value = null; // 입력창 닫기
  } catch (error) {
    console.error("대댓글 작성 시 오류:", error);
  }
};

// 모달이 열릴 때 댓글 목록 불러오기
onMounted(() => {
  loadComments();
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 50%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  text-align: left;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 20px;
  background-color: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

.add-comment input {
  width: 70%;
  padding: 10px;
  margin-right: 5px;
}

.add-comment button {
  background: #fba1b7;
  border: none;
  padding: 10px;
  border-radius: 5px;
  color: white;
  cursor: pointer;
}

.comments-container {
  margin-top: 20px;
}

.comment {
  border-bottom: 1px solid #ddd;
  padding: 10px 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.profile-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #ccc;
}

.reply-btn {
  text-align: right;
}

.reply-input {
  margin-top: 10px;
}

.reply-input input {
  width: 70%;
  padding: 5px;
  margin-right: 5px;
}

.reply-input button {
  background: #fba1b7;
  border: none;
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

.replies {
  margin-left: 20px;
  padding-left: 10px;
  border-left: 2px solid #ddd;
  margin-top: 20px;
}

img {
  width: 20px;
  height: 20px;
}
</style>
