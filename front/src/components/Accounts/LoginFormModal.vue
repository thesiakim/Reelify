// LoginFormModal.vue

<template>
  <div>
    <div class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeModal">x</button>
        <h2 class="modaltitle">로그인</h2>
        <div class="loginForm-container">
          <form @submit.prevent="logIn">
            <label for="username">사용자 이름</label><br />
            <input
              type="text"
              id="username"
              v-model.trim="username"
            /><br /><br />
            <label for="password">비밀번호</label><br />
            <input type="password" id="password" v-model.trim="password" />
            <br /><br />
            <input type="submit" value="로그인" />
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAccountStore } from "@/stores/accounts";

const store = useAccountStore();
const username = ref(null);
const password = ref(null);

const logIn = function () {
  const payload = {
    username: username.value,
    password: password.value,
  };
  store.logIn(payload);
};

const emit = defineEmits(["close"]);

const closeModal = () => {
  emit("close");
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7); /* 반투명 검정 배경 */
  display: flex;
  justify-content: center; /* 수평 중앙 정렬 */
  align-items: center; /* 수직 중앙 정렬 */
  z-index: 1000; /* 다른 요소 위에 표시 */
}

/* 모달 내용 박스 */
.modal-content {
  position: relative; /* 닫기 버튼을 절대 위치로 배치하기 위해 relative 설정 */
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 30vw;
  height: 45vh;
  max-width: 400px; /* 최대 너비 설정 */
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 닫기 버튼 */
.close-btn {
  position: absolute;
  top: 5px;
  right: 20px;
  background-color: white;
  border: none;
  font-size: 24px;
  font-weight: bold;
  color: #333;
  cursor: pointer;
}
</style>
