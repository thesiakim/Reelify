<template>
  <div class="chat-container">
    <h1 class="bot-name">ReelBot</h1>
    <div class="chat-box">
      <div v-for="(message, index) in messages" :key="index" class="message">
        <p>
          <strong v-if="message.isBot">ReelBot:</strong>
          <strong v-else>You:</strong> {{ message.text }}
        </p>
      </div>
    </div>
    <input
      v-model="userInput"
      type="text"
      placeholder="Type your message..."
      @keyup.enter="sendMessage"
    />
    <button @click="sendMessage">Send</button>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

// 상태 관리
const userInput = ref("");
const messages = ref([
  {
    text: "안녕하세요! 저는 ReelBot이에요. 영화 추천이 필요하거나 영화에 대해 궁금한 점이 있으면 언제든지 말해주세요!",
    isBot: true,
  },
]);

// 메시지 전송 함수
const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  // 사용자 메시지 추가
  messages.value.push({ text: userInput.value, isBot: false });

  try {
    // Django API 호출
    const response = await axios.post("http://127.0.0.1:8000/api/chatbot/", {
      message: userInput.value,
    });

    // 봇 응답 추가
    messages.value.push({ text: response.data.response, isBot: true });
  } catch (error) {
    console.error("Error:", error);
    messages.value.push({
      text: "Error: Unable to get a response.",
      isBot: true,
    });
  } finally {
    // 입력 필드 초기화
    userInput.value = "";
  }
};
</script>

<style scoped>
.chat-container {
  max-width: 650px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
  border-radius: 10px;
  border: 2px solid #e0e0e0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background: linear-gradient(to bottom, #ffccea, #fef9f2, #cde990);
}
.bot-name {
  font-size: 55px;
  font-weight: bold;
  color: white;
}
.chat-box {
  border: 3px solid white;
  padding: 10px;
  margin-bottom: 30px;
  height: 400px;
  width: 100%;
  overflow-y: scroll;
  border-radius: 8px;
  background-color: white;
}

.message {
  margin-bottom: 5px;
}

input {
  width: calc(100% - 22px);
  padding: 10px;
  margin-bottom: 10px;
  border: 3px solid #fef9f2;
  border-radius: 8px;
}

input:focus {
  border-color: #cde990;
  box-shadow: 0 0 5px #cde990;
  border-radius: 8px;
  outline: none;
}

button {
  padding: 10px 20px;
  background-color: #ffccea;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}
</style>
