<template>
  <div class="container my-5">
    <h1>{{ userData.username }}님이 작성한 리뷰와 댓글</h1>
    <hr />
    <!-- 리뷰 -->
    <h3>리뷰</h3>
    <div class="d-flex flex-column align-items-center">
      <UserReviewCard
        v-for="review in userData.written_reviews"
        :key="review.id"
        :review="review"
      />
    </div>
    <hr />
    <!-- 댓글 -->
    <div class="mb-4">
      <h3>댓글</h3>
      <div
        class="row comment-container d-flex justify-content-center"
        v-if="userData.written_comments && userData.written_comments.length > 0"
      >
        <UserCommentCard
          class="col-sm-6 mb-3 mb-sm-0 mx-3 my-3"
          v-for="comment in userData.written_comments"
          :key="comment.id"
          :comment="comment"
        />
      </div>
      <div
        v-else-if="
          userData.written_comments && userData.written_comments.length === 0
        "
      >
        <h4 class="text-center">아직 댓글을 작성하지 않았어요!😯</h4>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import axios from "axios";
import { useAccountStore } from "@/stores/accounts";
import { useRoute } from "vue-router";
import UserReviewCard from "@/components/Community/UserReviewCard.vue";
import UserCommentCard from "@/components/Community/UserCommentCard.vue";

const store = useAccountStore();
const route = useRoute();
const userData = ref([]);

onMounted(() => {
  axios({
    method: "get",
    url: `${store.API_URL}/api/v1/user-page/${route.params.username}/`,
  })
    .then((res) => {
      userData.value = res.data;
    })
    .catch((err) => {
      console.log(err);
    });
});
</script>

<style scoped>
.comment-container {
  margin-top: 20px;
  margin-bottom: 40px;
}
</style>
