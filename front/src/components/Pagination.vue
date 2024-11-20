<template>
  <div class="pagination">
    <button @click="goToPage(previousPage)" :disabled="!previousPage">
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

    <button @click="goToPage(nextPage)" :disabled="!nextPage">다음</button>
  </div>
</template>

<script>
export default {
  props: {
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
  },
  computed: {
    pageNumbers() {
      const startPage = (this.pageGroup - 1) * this.groupSize + 1;
      const endPage = Math.min(
        this.pageGroup * this.groupSize,
        this.totalPages
      );
      const pageNumbers = [];
      for (let i = startPage; i <= endPage; i++) {
        pageNumbers.push(i);
      }
      return pageNumbers;
    },
    previousPage() {
      return this.currentPage > 1 ? this.currentPage - 1 : null;
    },
    nextPage() {
      return this.currentPage < this.totalPages ? this.currentPage + 1 : null;
    },
  },
  methods: {
    goToPage(page) {
      this.$emit("page-changed", page);
    },
  },
};
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
}
</style>
