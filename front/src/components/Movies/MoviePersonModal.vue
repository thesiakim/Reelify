<template>
  <div v-if="isOpen" class="modal-container" @click.self="closeModal">
    <div class="modal-content" @click.stop>
      <!-- 모달 상단 X 버튼 -->
      <button class="close-btn" @click="closeModal">✖</button>
      <h2 v-if="personName">{{ personName }}의 영화를 찾으셨나요?</h2><br>
      <div class="movies-grid">
        <!-- 데이터가 준비되지 않은 경우 처리 -->
        <div v-if="!movies || movies.length === 0">
          <p>영화 데이터가 없습니다.</p>
        </div>
        <div
          class="movie-item"
          v-for="movie in movies"
          :key="movie.id"
        >
          <img
            v-if="movie.poster_path"
            :src="store.getPosterPath(movie.poster_path)"
            :alt="movie.title"
            @click="goToMovieDetail(movie.id)"
          />
          <p>{{ movie.title }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import axios from "axios";
import { useAccountStore } from "@/stores/accounts";
import { useRouter } from "vue-router";

const store = useAccountStore();
const router = useRouter();

const props = defineProps({
  isOpen: Boolean,
  personId: Number,
  personName: String,
  personType: String, // actor, director
  onClose: Function,
});

const movies = ref([]); // 빈 배열로 초기화

const fetchMovies = async () => {
  try {
    console.log("fetchMovies 호출");
    const response = await axios.get(
      `${store.API_URL}/api/v1/movies/${props.personType}/${props.personId}/`
    );
    console.log(response.data);
    movies.value = response.data || []; // 응답 데이터를 movies에 할당
    console.log("movies에 할당된 데이터:", movies.value);
  } catch (error) {
    console.error("배우/감독의 영화 목록 조회 중 에러 발생:", error);
    movies.value = [];
  }
};

// 모달 열림 상태를 감시
watch(
  () => props.isOpen,
  (newValue) => {
    if (newValue) {
      console.log("모달 열림, fetchMovies 호출");
      fetchMovies();
    } else {
      // 모달 닫힐 때 데이터 초기화
      movies.value = [];
    }
  }
);

const closeModal = () => {
  console.log("closeModal 호출");
  if (props.onClose) {
    props.onClose(); // 부모 컴포넌트의 closePersonModal 호출
  } else {
    console.error("props.onClose가 정의되지 않았습니다.");
  }
};

// const goToMovieDetail = (movieId) => {
//   console.log("Navigating to movie detail with ID:", movieId);
//   try {
//     router.push({ name: "MovieDetailView", params: { movie_id: String(movieId) } });
//   } catch (error) {
//     console.error("Error navigating to MovieDetailView:", error);
//   }
// };

const goToMovieDetail = (movieId) => {
  console.log(movieId)
};

</script>

<style scoped>
.modal-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* 최상위로 설정 */
}

.modal-content {
  background: #fff;
  padding: 15px;
  border-radius: 30px;
  width: 50%; /* 모달 창 너비 */
  max-height: 70%; /* 모달 창 최대 높이 */
  overflow-y: auto; /* 세로 스크롤 활성화 */
  position: relative;
  z-index: 10000; /* 모달 내용이 컨테이너보다 위에 있도록 설정 */
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  z-index: 10001; /* 닫기 버튼이 항상 위에 표시되도록 설정 */
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 5px; /* 포스터 간격을 매우 좁게 조정 */
  justify-content: center;
  width: 100%;
  padding: 0 10px; /* 양쪽 약간의 패딩 */
}


.movie-item img {
  width: 180px; /* 약간 크기 조정 */
  height: 270px; /* 높이 조정 */
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 3px 5px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s;
}

.movie-item p {
  text-align: center;
  margin-top: 5px;
  font-size: 0.85rem;
  color: #333;
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.movie-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 5px; /* 수직 간격 줄임 */
}


.movie-item img {
  width: 200px; /* 포스터 너비 확대 */
  height: 300px; /* 포스터 높이 확대 (3:2 비율) */
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s;
}

.movie-item img:hover {
  transform: scale(1.05); /* 마우스 오버 시 확대 */
}

h2 {
  font-weight: 800; /* 글자 두께를 더 굵게 설정 */
  font-size: 2rem; /* 글자 크기를 조금 더 키움 */
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 10px;

  /* 그라데이션 설정 */
  background: linear-gradient(135deg, #FBA1B7, #CDE990);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; /* 텍스트 색상을 투명으로 설정 */
  background-clip: text;
  text-fill-color: transparent;

  border-bottom: none;
  padding-bottom: 0;
}


</style>
