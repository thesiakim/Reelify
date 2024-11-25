<template>
  <div class="container text-center d-flex flex-column align-items-center my-3">
    <h1>내 정보 수정</h1>
    <div class="form-container d-flex flex-column justify-content-center">
      <form
        class="d-flex align-items-center flex-column"
        @submit.prevent="accountUpdate"
      >
        <h3>비밀번호 변경</h3>
        <div class="form-group mt-3">
          <label class="mb-2" for="oldPassword">기존 비밀번호</label><br />
          <input
            class="form-control"
            type="password"
            id="oldPassword"
            v-model.trim="oldPassword"
            placeholder="기존 비밀번호를 입력하세요"
          /><br />
          <span class="text-danger" v-if="errorMessage.oldPassword">{{
            errorMessage.oldPassword
          }}</span>
        </div>
        <div class="form-group mb-3">
          <label class="mb-2" for="newPassword1">새로운 비밀번호</label><br />
          <input
            class="form-control"
            type="password"
            id="newPassword1"
            v-model.trim="newPassword1"
            placeholder="새로운 비밀번호를 입력하세요"
          />
          <span class="text-danger" v-if="errorMessage.newPassword1">{{
            errorMessage.newPassword1
          }}</span>
        </div>

        <div class="form-group mb-4">
          <label class="mb-2" for="newpassword2">비밀번호 확인</label><br />
          <input
            class="form-control"
            type="password"
            id="newpassword2"
            v-model.trim="newPassword2"
            placeholder="다시 한 번 입력하세요"
          />
          <span class="text-danger" v-if="errorMessage.newPassword2">{{
            errorMessage.newPassword2
          }}</span>
        </div>

        <button type="submit" class="updatae-btn">회원정보 수정</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useAccountStore } from "@/stores/accounts";
import axios from "axios";
import { ref, watch } from "vue";

const store = useAccountStore();

const oldPassword = ref(null);
const newPassword1 = ref(null);
const newPassword2 = ref(null);

const errorMessage = ref({
  oldPassword: null,
  newPassword1: null,
  newPassword2: null,
});

// 실시간으로 새로운 비밀번호 검증하기
watch(newPassword1, () => {
  validateNewPassword();
});

// 비밀번호 검증 함수
const validateNewPassword = () => {
  // 초기화
  errorMessage.value.newPassword1 = null;

  // 비밀번호 최소 길이 검증 (예: 8자 이상)
  if (newPassword1.value && newPassword1.value.length < 8) {
    errorMessage.value.newPassword1 = "비밀번호는 최소 8자 이상이어야 합니다.";
  }
};

const validatePasswords = () => {
  let isValid = true;

  // 초기화
  errorMessage.value.oldPassword = null;
  errorMessage.value.newPassword1 = null;
  errorMessage.value.newPassword2 = null;

  // 비밀번호 확인
  if (
    newPassword1.value &&
    newPassword2.value &&
    newPassword1.value !== newPassword2.value
  ) {
    errorMessage.value.newPassword2 =
      "새로운 비밀번호와 확인 비밀번호가 일치하지 않습니다.";
    isValid = false;
  }

  return isValid;
};
const accountUpdate = function () {
  if (!validatePasswords()) {
    return; // 검증 실패 시 함수 종료
  }

  const payload = {
    old_password: oldPassword.value,
    new_password1: newPassword1.value,
    new_password2: newPassword2.value,
  };
  store.UserUpdate(payload);
};
</script>

<style scoped>
.form-container {
  border-radius: 10px;
  background: linear-gradient(to bottom, #ffccea, #fef9f2, #cde990);
  margin-top: 50px;
  width: 430px;
  height: 450px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 그림자 효과 */
}
.form-group {
  width: 380px;
  font-weight: bold;
}
.form-control {
  width: 100%;
}

.form-control:focus {
  border-color: #fba1b7; /* 입력칸 테두리 색상 */
  box-shadow: 0 0 5px #fba1b7; /* 강조 효과 */
  outline: none; /* 기본 파란색 테두리 제거 */
}
.updatae-btn {
  border: transparent;
  border-radius: 10px;
  background-color: #a1eebd;
  color: white;
  font-weight: bold;
  width: 120px;
  height: 30px;
}
</style>
