<template>
  <div class="signup-container my-5 d-flex justify-content-center">
    <div class="signup-box">
      <h1 class="signup-title">회원가입</h1>
      <form @submit.prevent="validateSignUp">

        <!-- 이메일 입력 필드 -->
        <div class="form-group">
          <label for="email">이메일</label>
          <input
            type="email"
            id="email"
            v-model="email"
            class="form-control"
            placeholder="이메일을 입력하세요"
          />
          <!-- 이메일 에러 메시지 출력 -->
          <span v-if="emailError" class="text-danger">{{ emailError }}</span>
          <button @click.prevent="sendVerificationCode">
            {{ verificationSent ? "재전송" : "인증번호 받기" }}
          </button>
        </div>
        <div>
          <!-- 인증번호 입력 필드: 인증번호 발송 후 활성화 -->
          <div v-if="verificationSent">
            <label for="verification-code">인증번호</label>
            <input
              type="text"
              id="verification-code"
              v-model="verificationCode"
              class="form-control"
              placeholder="인증번호를 입력하세요"
            />
          </div>
          
          <!-- 인증번호 에러 메시지: 항상 표시 -->
          <span v-if="verificationCodeError" class="text-danger">{{ verificationCodeError }}</span>
        </div>




        
        <div class="form-group">
          <label for="username">사용자 별명</label>
          <input
            type="text"
            id="username"
            v-model.trim="username"
            class="form-control"
            placeholder="사용자 별명을 입력하세요"
          />
          <span v-if="usernameError" class="text-danger">{{ usernameError }}</span>
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
          <span v-if="passwordError" class="text-danger">{{ passwordError }}</span>
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
          <span v-if="passwordError2" class="text-danger">{{ passwordError2 }}</span>
        </div>

        <div class="form-group">
          <label>좋아하는 장르를 선택하세요</label>
          <p v-if="movieError" class="text-danger">{{ movieError }}</p>
          <p v-else class="text-custom">현재 선택한 영화는 {{ selectedMovies.length }}개 입니다.</p>
          <div class="genre-button-container">
            <button
              v-for="group in genreGroups"
              :key="group.name"
              class="btn genre-btn m-2"
              @click.prevent="openModal(group.ids)"
            >
              {{ group.name }}
            </button>
          </div>
        </div>

        <button type="submit" class="btn btn-primary mt-3">등록</button>
      </form>
    </div>

    <!-- MovieSignUpModal -->
    <MovieSignUpModal
      v-if="showModal"
      :show="showModal"
      :genreIds="selectedGenreIds"
      :alreadySelectedMovies="selectedMovies"
      @close="closeModal"
      @moviesSelected="handleMoviesSelected"
    />
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useAccountStore } from "@/stores/accounts";
import MovieSignUpModal from "@/components/Movies/MovieSignUpModal.vue";

const store = useAccountStore();
const router = useRouter();

const email = ref(null);
const verificationCode = ref(null)
const verificationSent = ref(false);
const verificationCodeError = ref(null);
const username = ref(null);
const password1 = ref(null);
const password2 = ref(null);
const movieError = ref(null);

// 에러 메시지
const emailError = ref(null);
const usernameError = ref(null);
const passwordError = ref(null);
const passwordError2 = ref(null);

const genreGroups = [
  { name: "모험 & 판타지", ids: [12, 14] },
  { name: "로맨스", ids: [10749] },
  { name: "드라마 & 코미디", ids: [18, 35] },
  { name: "애니메이션 & TV 영화", ids: [16, 10770] },
  { name: "음악 & 가족", ids: [10402, 10751] },
  { name: "공포 & 스릴러", ids: [27, 53] },
  { name: "SF & 미스터리", ids: [878, 9648] },
  { name: "액션 & 범죄", ids: [28, 80] },
  { name: "역사 & 다큐멘터리", ids: [36, 99] },
  { name: "서부 & 전쟁", ids: [37, 10752] },
];

const showModal = ref(false);
const selectedGenreIds = ref([]);
const selectedMovies = ref([]);

const openModal = (genreIds) => {
  selectedGenreIds.value = genreIds;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};


const signUp = () => {
  const payload = {
    username: username.value,
    password1: password1.value,
    password2: password2.value,
    selectedMovies: selectedMovies.value,
    email: email.value,
    verification_code: verificationCode.value,
  };

  axios
    .post(`${store.API_URL}/accounts/signup/`, payload)
    .then(() => {
      console.log("회원가입 성공");
      const password = password1.value;
      store.logIn({ username: username.value, password });
      router.push({ name: "HomeView" });
    })
    .catch((err) => {
      console.log("서버 응답:", err.response.data); // 응답 데이터 확인
      if (err.response && err.response.data) {
        emailError.value = null;
        verificationCodeError.value = null;
        usernameError.value = null;
        passwordError.value = null;
        passwordError2.value = null;

        // 인증번호 관련 에러 처리
        if (err.response.data.verification_code) {
          const verificationError = err.response.data.verification_code[0];
          if (verificationError === "인증번호가 일치하지 않습니다.") {
            verificationCodeError.value = "인증번호가 일치하지 않습니다.";
          } else if (verificationError === "This field may not be null.") {
            verificationCodeError.value = "이메일을 인증해주세요";
          } else {
            verificationCodeError.value = verificationError; // 기타 에러 메시지
          }
        }

        // 이메일 에러 처리
        if (err.response.data.email) {
          emailError.value = "올바른 이메일 형식으로 입력해주세요."
        }
        // 사용자 이름 에러 처리
        if (err.response.data.username) {
          usernameError.value = "이미 존재하는 사용자 이름입니다.";
        }
        // 비밀번호 에러 처리
        if (err.response.data.password1) {
          passwordError.value = "비밀번호는 최소 8글자 이상이어야 합니다.";
        }
        // 기타 에러 처리
        if (err.response.data.non_field_errors) {
          passwordError.value = "비밀번호가 일치하지 않습니다.";
        }
      } else {
        console.error("서버와의 연결에 문제가 발생했습니다. 다시 시도해주세요.");
      }
    });
};






const validateSignUp = () => {
  let hasError = false;

  // 이메일 검증
  if (!email.value) {
    emailError.value = "이메일을 입력해주세요";
    hasError = true;
  } else {
    emailError.value = null;
  }

  // 사용자 이름 검증
  if (!username.value) {
    usernameError.value = "별명을 입력해주세요";
    hasError = true;
  } else {
    usernameError.value = null;
  }

  // 비밀번호 검증
  if (!password1.value) {
    passwordError.value = "비밀번호를 입력해주세요";
    hasError = true;
  } else {
    passwordError.value = null;
  }

  // 비밀번호 확인 검증
  if (!password2.value) {
    passwordError2.value = "비밀번호를 다시 입력해주세요";
    hasError = true;
  } else if (password1.value !== password2.value) {
    passwordError2.value = "비밀번호가 일치하지 않습니다.";
    hasError = true;
  } else {
    passwordError2.value = null;
  }

  // 영화 선택 검증
  if (selectedMovies.value.length < 10) {
    movieError.value = "10개의 영화를 선택해주세요";
    hasError = true;
  } else {
    movieError.value = null;
  }

  if (!hasError) {
    signUp();
  }
};

const handleMoviesSelected = (movies) => {
  selectedMovies.value = movies;

  // 선택된 영화가 존재하면 에러 메시지 제거
  if (selectedMovies.value.length > 0) {
    movieError.value = null;
  }

  console.log("현재 선택된 영화:", selectedMovies.value);
};



// 사용자 입력을 감지하여 에러 메시지 초기화
watch(username, (newVal) => {
  if (newVal) {
    usernameError.value = null;
  }
});

watch(password1, (newVal) => {
  if (newVal) {
    passwordError.value = null;
  }
});

watch(password2, (newVal) => {
  if (newVal) {
    passwordError2.value = null;
  }
});

watch(password1, (newPassword) => {
  if (!newPassword) {
    passwordError.value = "비밀번호를 입력해주세요";
  } else {
    passwordError.value = null;
  }

  // 비밀번호 확인과 일치 여부도 동시에 검증
  if (password2.value && newPassword !== password2.value) {
    passwordError2.value = "비밀번호가 일치하지 않습니다.";
  } else {
    passwordError2.value = null;
  }
});

watch(password2, (newPasswordConfirm) => {
  if (!newPasswordConfirm) {
    passwordError2.value = "비밀번호를 다시 입력해주세요";
  } else if (password1.value !== newPasswordConfirm) {
    passwordError2.value = "비밀번호가 일치하지 않습니다.";
  } else {
    passwordError2.value = null;
  }
});

const sendVerificationCode = () => {
  axios
    .post(`${store.API_URL}/api/v1/email-verification/`, { email: email.value })
    .then((response) => {
      alert(response.data.message); 
      verificationSent.value = true;  // 인증번호 입력 필드 활성화
    })
    .catch((error) => {
      alert(error.response.data.error || "오류가 발생했습니다. 다시 시도해주세요.");
    });
};
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
  border-color: #fba1b7;        /* 입력칸 테두리 색상 */
  box-shadow: 0 0 5px #fba1b7;  /* 강조 효과 */
  outline: none;                  /* 기본 파란색 테두리 제거 */
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

.genre-btn {
  border: 1px solid #e98fa5;
  color: #e98fa5;
  background-color: transparent;
  transition: all 0.3s ease;
}

.genre-btn:hover {
  background-color: #fba1b7;
  color: #fff;
}

.text-custom {
  color: darkgrey;
  font-size: 14px;
  padding-left: 6px;
}
</style>
