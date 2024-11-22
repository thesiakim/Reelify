<template>
  <div class="custom-alert">
    <div class="alert-content">
      <p>{{ message }}</p>
      <button @click="closeModal">확인</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["close"]);

const closeModal = () => {
  emit("close"); 
};
</script>

<style scoped>
.custom-alert {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5); /* 반투명 배경 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.alert-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.alert-content p {
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
}

.alert-content button {
  background: #fba1b7;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.alert-content button:hover {
  background: #e08fa5;
}
</style>
