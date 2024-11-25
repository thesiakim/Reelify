<template>
  <div>
    <div class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeModal">x</button>
        <h2 class="modal-title">로그인</h2>
        <div class="loginForm-container">
          <form @submit.prevent="logIn">
            <label for="username" class="form-label">사용자 이름</label>
            <input
              type="text"
              id="username"
              v-model.trim="username"
              class="form-input"
              placeholder="아이디를 입력하세요"
            />
            <label for="password" class="form-label">비밀번호</label>
            <input
              type="password"
              id="password"
              v-model.trim="password"
              class="form-input"
              placeholder="비밀번호를 입력하세요"
            />
            <div class="error-message-container">
              <span v-if="errorMessage" class="error-message">{{
                errorMessage
              }}</span>
            </div>
            <input type="submit" value="확인" class="submit-btn" />
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAccountStore } from "@/stores/accounts";
import { useRouter } from "vue-router";

const store = useAccountStore();
const username = ref(null);
const password = ref(null);
const errorMessage = ref(""); // 에러 메시지 상태
const router = useRouter();

const logIn = async function () {
  const payload = {
    username: username.value,
    password: password.value,
  };

  await store.logIn(payload); // 비동기 호출
  if (store.loginResult) {
    closeModal();
    router.push({ name: "HomeView" });
  } else {
    errorMessage.value = "이름 또는 비밀번호를 다시 확인해주세요."; // 에러 메시지 설정
  }
};

const emit = defineEmits(["close"]);

const closeModal = () => {
  emit("close");
};
</script>

<style scoped>
/* 전체 배경 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7); /* 반투명 검정 배경 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* 모달 창 */
.modal-content {
  position: relative;
  background-color: #ffffff;
  padding: 30px 20px;
  border-radius: 15px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
  text-shadow: none !important;
}

/* 입력 필드 */
.form-label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 5px;
  text-align: left;
  text-shadow: none !important;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-bottom: 20px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #fba1b7;
  outline: none;
  box-shadow: 0px 0px 5px rgba(251, 161, 183, 0.5);
}

/* 에러 메시지 */
.error-message-container {
  margin-bottom: 10px;
}

.error-message {
  color: #ff4d4f;
  font-size: 13px;
}

/* 로그인 버튼 */
.submit-btn {
  background-color: #fba1b7;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  width: 100%;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background-color: #e890a3;
}

/* 닫기 버튼 */
.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 20px;
  font-weight: bold;
  color: #888;
  cursor: pointer;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #333;
}
</style>
