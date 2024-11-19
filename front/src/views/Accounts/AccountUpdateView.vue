<template>
  <div>
    <h1>회원정보 수정</h1>
    <form @submit.prevent="accountUpdate">
      <label for="newPassword1">새로운 비밀번호</label><br>
      <input type="password" id="newPassword1" v-model.trim="newPassword1"><br><br>
      
      <label for="newpassword2">비밀번호 확인</label><br>
      <input type="password" id="newpassword2" v-model.trim="newPassword2"><br><br>

      <input type="text">
    </form>
  </div>
</template>

<script setup>
import { useAccountStore } from '@/stores/accounts';

const store = useAccountStore()

const newPassword1 = ref(null)
const newPassword2 = ref(null)


const accountUpdate = function() {
  const payload = {
    password1: newPassword1.value,
    password2: newPassword2.values
  }
  // 스토어 함수 요청
}


</script>

<style scoped></style>
