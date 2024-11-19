import { ref, computed } from "vue";
import { defineStore } from "pinia";
import axios from "axios";

export const useAccountStore = defineStore("account", () => {
  const API_URL = "http://127.0.0.1:8000";
  const token = ref(null)

  // 회원 관련 ===============================================================================================

  // 회원 가입
  const errorMessage = ref(null);
  const signUp = function (payload) {
    const { username, password1, password2 } = payload;

    errorMessage.value = null;
    axios({
      method: "post",
      url: `${API_URL}/accounts/signup/`,
      data: {
        username,
        password1,
        password2,
      },
    })
      .then((res) => {
        const password = password1;
        logIn({ username, password }); // 회원가입 성공 시 자동 로그인
      })
      .catch((err) => {
        if (err.response && err.response.data) {
          if (err.response.data.username) {
            errorMessage.value = "이미 존재하는 사용자 이름입니다.";
          } else if (err.response.data.non_field_errors) {
            errorMessage.value = "비밀번호가 일치하지 않습니다.";
          } else if (err.response.data.password1) {
            errorMessage.value = "비밀번호는 최소 6글자 이상이어야 합니다.";
          } else {
            errorMessage.value = "알 수 없는 오류가 발생했습니다.";
          }
        } else {
          errorMessage.value =
            "서버와의 연결에 문제가 발생했습니다. 다시 시도해주세요.";
        }
        console.log(err);
      });
  };

  // 로그인
  const logIn = function (payload) {
    const { username, password } = payload
    
    axios({
      method: 'post',
      url: `${API_URL}/accounts/login/`,
      data: {
        username, password
      }
    })
      .then(res => {
        console.log('로그인이 완료되었습니다')
        token.value = res.data.key
      })
      .catch(err => console.log(err))
  }

  // 영화 관련 ===============================================================================================

  // 검색 결과 저장 
  const searchResults = ref([])

  // 이미지 경로 반환
  const getPosterPath = (path) => {
    const TMDB_URL = "https://image.tmdb.org/t/p/w780"; // TMDB 이미지 베이스 URL
    return `${TMDB_URL}${path}`;
  };

  return { signUp, errorMessage, logIn, token, API_URL, getPosterPath, searchResults  };
});
