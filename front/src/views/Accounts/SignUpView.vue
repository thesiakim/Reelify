<template>
  <div class="signup-container mt-5 d-flex justify-content-center">
    <div class="signup-box">
      <h1 class="signup-title">회원가입</h1>
      <form @submit.prevent="validateSignUp">
        <div class="form-group">
          <label for="username">사용자 별명</label>
          <input
            type="text"
            id="username"
            v-model.trim="username"
            class="form-control"
            placeholder="사용자 별명을 입력하세요"
          />
          <span v-if="usernameError" class="text-danger">{{
            usernameError
          }}</span>
        </div>

        <div class="form-group">
          <label for="password1">비밀번호</label>
          <input
            type="password"
            id="password1"
            v-model.trim="password1"
            class="form-control"
            placeholder="비밀번호를 입력하세요"
          />
          <span v-if="passwordError" class="text-danger">{{
            passwordError
          }}</span>
        </div>

        <div class="form-group">
          <label for="password2">비밀번호 확인</label>
          <input
            type="password"
            id="password2"
            v-model.trim="password2"
            class="form-control"
            placeholder="비밀번호를 다시 입력하세요"
          />
          <span v-if="passwordError2" class="text-danger">{{
            passwordError2
          }}</span>
        </div>

        <div class="form-group">
          <label>좋아하는 영화 5개를 선택해주세요</label>
          <div class="movies-container">
            <div
              v-for="movie in movies"
              :key="movie.id"
              class="movie-card"
              :class="{ selected: selectedMovies.includes(movie.id) }"
              @click="toggleMovieSelection(movie.id)"
            >
              <img
                :src="store.getPosterPath(movie.poster_path)"
                :alt="movie.title"
              />
              <p>{{ movie.title }}</p>
            </div>
          </div>
          <span v-if="movieError" class="text-danger">{{ movieError }}</span>
        </div>

        <button type="submit" class="btn btn-primary mt-3">회원가입</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import { useAccountStore } from "@/stores/accounts";
import { useRouter } from "vue-router";

const store = useAccountStore();
const router = useRouter()

const username = ref(null);
const password1 = ref(null);
const password2 = ref(null);
const movies = ref([]);
const selectedMovies = ref([]);
const movieError = ref(null);

// 에러 메시지
const usernameError = ref(null);
const passwordError = ref(null);
const passwordError2 = ref(null);

// 영화 데이터 요청
onMounted(() => {
  axios({
    url: "http://127.0.0.1:8000/api/v1/movies/sample/",
    method: "get",
  })
    .then((response) => {
      movies.value = response.data;
    })
    .catch((error) => {
      console.log(`회원 가입 시 샘플 영화 조회 에러 : ${error}`);
    });
});

// 영화 선택 토글
const toggleMovieSelection = (movieId) => {
  if (selectedMovies.value.includes(movieId)) {
    selectedMovies.value = selectedMovies.value.filter((id) => id !== movieId);
  } else if (selectedMovies.value.length < 5) {
    selectedMovies.value.push(movieId);
  }
};

// 회원가입 요청 함수
const signUp = () => {
  const payload = {
    username: username.value,
    password1: password1.value,
    password2: password2.value,
    selectedMovies: selectedMovies.value,
  };

  // 초기화
  usernameError.value = null;
  passwordError.value = null;

  axios({
    method: "post",
    url: `${store.API_URL}/accounts/signup/`,
    data: payload,
  })
    .then(() => {
      console.log("회원가입 성공");
      const password = password1.value;
      store.logIn({ username: username.value, password }); // 자동 로그인
      router.push({ name: 'HomeView'})
    })
    .catch((err) => {
      if (err.response && err.response.data) {
        if (err.response.data.username) {
          usernameError.value = "이미 존재하는 사용자 이름입니다.";
        }
        if (err.response.data.password1) {
          passwordError.value =
            "비밀번호는 최소 9글자 이상이고 숫자와 문자를 모두 사용해야 합니다.";
        }
        if (err.response.data.non_field_errors) {
          passwordError.value = "비밀번호가 일치하지 않습니다.";
        }
      } else {
        console.error(
          "서버와의 연결에 문제가 발생했습니다. 다시 시도해주세요."
        );
      }
    });
};

// 회원가입 유효성 검사
const validateSignUp = () => {
  if (selectedMovies.value.length < 5) {
    movieError.value = "5개의 영화를 선택해주세요";
  } else {
    movieError.value = null;
    signUp();
  }
};

// 사용자 이름 실시간 유효성 검사
watch(username, () => {
  if (!username.value) {
    usernameError.value = "사용자 별명은 필수입니다.";
  } else if (username.value && username.value.length < 3) {
    usernameError.value = "사용자 별명은 최소 3글자 이상이어야 합니다.";
  } else {
    usernameError.value = null;
  }
});

// 비밀번호1 실시간 유효성 검사
watch(password1, () => {
  if (password1.value && password1.value.length < 9) {
    passwordError.value = "비밀번호는 최소 9글자 이상이어야 합니다.";
  } else if (
    password1.value &&
    !/[A-Za-z]/.test(password1.value) &&
    !/\d/.test(password1.value)
  ) {
    passwordError.value = "비밀번호는 문자와 숫자를 모두 포함해야 합니다.";
  } else {
    passwordError.value = null;
  }
});

// 비밀번호2 실시간 유효성 검사
watch(password2, () => {
  if (password2.value !== password1.value) {
    passwordError2.value = "비밀번호가 일치하지 않습니다.";
  } else {
    passwordError2.value = null;
  }
});
</script>

<style scoped>
.signup-box {
  width: 40vw;
  min-height: 70vh;
  border: 3px solid #e0e0e0;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 30px;
  text-align: center;
}

.signup-title {
  font-size: 2rem;
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
  text-align: left;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.form-control:focus {
  border-color: #007bff;
  outline: none;
}

.movies-container {
  display: flex;
  flex-wrap: nowrap;
  gap: 15px;
  overflow-x: auto;
  padding: 10px 0;
}

.movies-container::-webkit-scrollbar {
  height: 8px;
}

.movies-container::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 10px;
}

.movies-container::-webkit-scrollbar-track {
  background-color: #f1f1f1;
}

.movie-card {
  flex: 0 0 auto;
  width: 120px;
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 10px;
  text-align: center;
  transition: transform 0.3s, border-color 0.3s;
}

.movie-card img {
  width: 100%;
  border-radius: 10px;
}

.movie-card p {
  font-size: 14px;
  margin-top: 8px;
}

.movie-card:hover {
  transform: scale(1.05);
}

.movie-card.selected {
  border-color: #e98fa5;
  transform: scale(1.05);
}

.btn-primary {
  background-color: #fba1b7;
  color: #fff;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #e98fa5;
}
</style>
