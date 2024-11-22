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
          @keyup.enter="addComment"
        />
        <button @click="addComment">작성</button>
      </div>

      <!-- 댓글 목록 -->
      <div class="comments-container">
        <h4>댓글 목록</h4>
        <div v-if="comments.length > 0">
          <div
            v-for="(comment, index) in comments"
            :key="comment.id"
            class="comment"
            :ref="index === comments.length - 1 ? setLastCommentRef : null"
          >
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

            <!-- 댓글, 대댓글 액션 버튼 -->
            <div class="comment-actions">
              <div class="reply-btn">
                <img
                  @click="toggleReplyInput(comment.id)"
                  src="@/assets/reply-icon.png"
                  alt="reply-icon.png"
                />
              </div>
              <button
                v-if="store.userName === comment.user.username"
                class="delete-btn"
                @click="deleteComment(comment.id)"
              >
                삭제
              </button>
            </div>

            <!-- 대댓글 입력칸 -->
            <div v-if="showReplyInput === comment.id" class="reply-input">
              <input
                type="text"
                v-model.trim="replyContent"
                placeholder="대댓글을 입력하세요"
                @keyup.enter="addReply(comment.id)"
              />
              <button @click="addReply(comment.id)">작성</button>
            </div>

            <!-- 대댓글 -->
            <div
              v-if="Array.isArray(comment.replies) && comment.replies.length > 0"
              class="replies"
            >
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
                <button
                  v-if="store.userName === reply.user.username"
                  class="delete-btn"
                  @click="deleteComment(reply.id)"
                >
                  삭제
                </button>
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
import { ref, onMounted, nextTick } from "vue";
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

// 상태 관리
const comments = ref([]);
const newComment = ref("");
const replyContent = ref("");
const showReplyInput = ref(null);

const page = ref(1);
const hasMore = ref(true);
const isLoading = ref(false);

const observer = ref(null);

const store = useAccountStore();
const API_URL = store.API_URL;
const token = store.token;

// 날짜 포맷 함수
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

// 댓글 목록 가져오기
const loadComments = async () => {
  if (!hasMore.value || isLoading.value) return; // 중복 호출 방지
  isLoading.value = true;

  try {
    const response = await axios.get(
      `${API_URL}/api/v1/movies/reviews/${props.reviewId}/comments/`,
      { params: { page: page.value } }
    );

    if (response.data.results && response.data.results.length > 0) {
      comments.value.push(...response.data.results); // 댓글 추가
      page.value += 1;
    } else {
      hasMore.value = false; // 추가 댓글 없음
    }
  } catch (error) {
    console.error("댓글 로드 오류:", error);
  } finally {
    isLoading.value = false;
  }
};

// IntersectionObserver 설정
const setLastCommentRef = (el) => {
  if (observer.value) observer.value.disconnect();

  observer.value = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMore.value && !isLoading.value) {
      loadComments(); // 마지막 요소가 보이면 호출
    }
  });

  if (el) observer.value.observe(el);
};

// 댓글 추가
const addComment = async () => {
  try {
    const response = await axios.post(
      `${API_URL}/api/v1/reviews/${props.reviewId}/comments/`,
      { content: newComment.value },
      { headers: { Authorization: `Token ${store.token}` } }
    );
    comments.value.unshift(response.data);
    newComment.value = "";
  } catch (error) {
    console.error("댓글 추가 오류:", error);
  }
};

// 대댓글 추가
const addReply = async (commentId) => {
  try {
    const response = await axios.post(
      `${API_URL}/api/v1/comments/${commentId}/replies/`,
      { content: replyContent.value },
      { headers: { Authorization: `Token ${store.token}` } }
    );
    const commentIndex = comments.value.findIndex((c) => c.id === commentId);
    if (commentIndex !== -1) {
      if (!comments.value[commentIndex].replies) {
        comments.value[commentIndex].replies = [];
      }
      comments.value[commentIndex].replies.push(response.data);
    }
    replyContent.value = "";
    showReplyInput.value = null;
  } catch (error) {
    console.error("대댓글 추가 오류:", error);
  }
};

// 대댓글 입력창 토글
const toggleReplyInput = (commentId) => {
  showReplyInput.value = showReplyInput.value === commentId ? null : commentId;
};

// 댓글, 대댓글 삭제
const deleteComment = (id) => {
  axios({
    method: "delete",
    url: `${store.API_URL}/api/v1/comments/${id}/`,
    headers: {
      Authorization: `Token ${token}`,
    },
  })
    .then(() => {
      console.log("댓글 삭제 완료");
      const commentIndex = comments.value.findIndex((comment) => comment.id === id);

      if (commentIndex !== -1) {
        comments.value.splice(commentIndex, 1);
        return;
      }

      comments.value.forEach((comment) => {
        if (Array.isArray(comment.replies)) {
          const replyIndex = comment.replies.findIndex((reply) => reply.id === id);
          if (replyIndex !== -1) {
            comment.replies.splice(replyIndex, 1);
          }
        }
      });
    })
    .catch((error) => {
      console.error(`댓글 삭제 중 에러 발생: ${error}`);
    });
};

onMounted(async () => {
  await nextTick();
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
  border-radius: 20px;
  width: 50%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  text-align: left;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  scrollbar-width: thin; /* Firefox용 */
  scrollbar-color: #fba1b7 white; /* Firefox용 */
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

.comment-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.reply-btn {
  display: flex;
  align-items: center;
}

.delete-btn {
  background: #fba1b7;
  border: none;
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.delete-btn:hover {
  background: #e08fa5;
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
