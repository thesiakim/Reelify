<template>
  <div>
    <img :src="movie.poster_path" alt="" />
  </div>
</template>

<script setup>
defineProps({
  movie: Object,
});
</script>

<style scoped></style>
