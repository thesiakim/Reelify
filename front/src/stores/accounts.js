import { ref, computed } from "vue";
import { defineStore } from "pinia";
import axios from "axios";

export const useAccountStore = defineStore("account", () => {
  const API_URL = "http://127.0.0.1:8000";
  const token = ref(null)

  // 회원 관련 ===============================================================================================

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

  // return { signUp, errorMessage, logIn, token, API_URL, getPosterPath, searchResults  };
  return { logIn, token, API_URL, getPosterPath, searchResults  };
});
