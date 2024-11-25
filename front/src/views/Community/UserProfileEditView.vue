<template>
  <div class="container text-center my-4">
    <h1>프로필 이미지 편집</h1>
    <h5>원하는 이미지를 선택해주세요!</h5>
    <form class="my-5" @submit.prevent="submitForm">
      <label for="profile-img">
        <input type="file" ref="fileInput" />
        <input type="submit" value="제출" />
      </label>
    </form>
  </div>
</template>

<script setup>
import { useAccountStore } from "@/stores/accounts.js";
import axios from "axios";
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const store = useAccountStore();
const router = useRouter();
const route = useRoute();
const fileInput = ref(null);

const submitForm = async () => {
  const formData = new FormData();
  // 파일이 선택되었는지 확인
  const file = fileInput.value?.files[0];
  if (!file) {
    alert("파일을 선택해주세요.");
    return;
  }

  // FormData에 파일 추가
  formData.append("profile_img", file);

  try {
    // axios로 파일 전송
    const response = await axios({
      method: "patch",
      url: `${store.API_URL}/api/v1/profile-image/`,
      headers: {
        Authorization: `Token ${store.token}`,
        "Content-Type": "multipart/form-data", // multipart/form-data로 요청
      },
      data: formData,
    });

    console.log("이미지 변경 완료");
    console.log(response.data);
    alert("이미지가 성공적으로 변경되었습니다.");
    router.push({
      name: "UserPageView",
      params: { username: route.params.username },
    });
  } catch (error) {
    console.error("이미지 변경 오류:", error);
    alert("이미지 변경에 실패했습니다.");
  }
};
</script>

<style scoped></style>
