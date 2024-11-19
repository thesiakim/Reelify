<template>
  <div class="signup-container mt-5 d-flex justify-content-center">
    <div class="signup-box">
      <h1>회원가입</h1>
      <form @submit.prevent="signUp">
        <label for="username">사용자 별명</label><br />
        <input type="text" id="username" v-model.trim="username" /><br /><br />

        <label for="password1">비밀번호</label><br />
        <input
          type="password"
          id="password1"
          v-model.trim="password1"
        /><br /><br />

        <label for="password2">비밀번호 확인</label><br />
        <input
          type="password"
          id="password2"
          v-model.trim="password2"
        /><br /><br />

        <input type="submit" value="회원가입" />
      </form>

      <div v-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useAccountStore } from "@/stores/accounts";

const store = useAccountStore();

const username = ref(null);
const password1 = ref(null);
const password2 = ref(null);

const signUp = function () {
  const payload = {
    username: username.value,
    password1: password1.value,
    password2: password2.value,
  };
  store.signUp(payload);
};

const errorMessage = computed(() => store.errorMessage);
</script>

<style scoped>
.signup-box {
  width: 40vw;
  height: 60vh;
  text-align: center;
  border: 3px solid #ffd1da;
  background-color: #ffd1da;
  border-radius: 10px;
  margin-top: 60px;
}

.error-message {
  color: red;
  margin-top: 20px;
}
</style>
