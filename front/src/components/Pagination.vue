<template>
  <div class="pagination">
    <button @click="goToPage(previousPage)" :disabled="previousPage === null">
      이전
    </button>

    <!-- 페이지 번호 출력 -->
    <button
      v-for="pageNumber in pageNumbers"
      :key="pageNumber"
      @click="goToPage(pageNumber)"
      :class="{ active: currentPage === pageNumber }"
    >
      {{ pageNumber }}
    </button>

    <button @click="goToPage(nextPage)" :disabled="nextPage === null">
      다음
    </button>
  </div>
</template>

<script setup>
import { computed, watch, onUpdated, defineProps, defineEmits } from "vue";

// props 선언
const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
  },
  totalPages: {
    type: Number,
    required: true,
  },
  pageGroup: {
    type: Number,
    required: true,
  },
  groupSize: {
    type: Number,
    required: true,
  },
});

// emits 선언
const emit = defineEmits(["page-changed"]);

// computed 값
const pageNumbers = computed(() => {
  const startPage = (props.pageGroup - 1) * props.groupSize + 1;
  const endPage = Math.min(props.pageGroup * props.groupSize, props.totalPages);
  const numbers = [];
  for (let i = startPage; i <= endPage; i++) {
    numbers.push(i);
  }
  return numbers;
});

const previousPage = computed(() =>
  props.currentPage > 1 ? props.currentPage - 1 : null
);
const nextPage = computed(() =>
  props.currentPage < props.totalPages ? props.currentPage + 1 : null
);

// 페이지 이동 함수
const goToPage = (page) => {
  if (page !== null && page >= 1 && page <= props.totalPages) {
    emit("page-changed", page);
  }
};

// 페이지 초기화
// watch 로 totalPages 변화 감지하여 처리
watch(
  () => props.totalPages,
  (newTotalPages) => {
    if (newTotalPages === 0) {
      emit("page-changed", 1);
    }
  }
);

// 페이지 숫자가 변경될 때마다 데이터가 업데이트된 후에 페이지 번호 배열이 새로 계산되도록 합니다.
onUpdated(() => {
  pageNumbers.value;
});
</script>

<style scoped>
.pagination {
  margin-top: 20px;
}

button {
  margin: 5px;
  padding: 10px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

button.active {
  background-color: #007bff;
  color: white;
  font-weight: bold;
  border-color: #007bff;
}
</style>
