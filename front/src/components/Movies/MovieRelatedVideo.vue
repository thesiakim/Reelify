<template>
  <div class="modal-overlay" v-if="isOpen" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="video-container">
        <iframe
          v-if="activeVideoUrl"
          :src="activeVideoUrl"
          frameborder="0"
          allow="autoplay; encrypted-media"
          allowfullscreen
        ></iframe>
      </div>
      <button class="close-button" @click="closeModal">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from "vue";

const props = defineProps({
  isOpen: Boolean,
  activeVideoUrl: String,
});

const emits = defineEmits(["close"]);

const closeModal = () => {
  emits("close");
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: transparent;
  padding: 20px;
  border-radius: 10px;
  position: relative;
  width: 80vw;
  height: 90vh;
  text-align: center;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}
.video-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.video-container iframe {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 10px;
}
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
}
</style>
