import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { useRouter } from "vue-router";
import axios from "axios";
import UserLikeMovie from "@/components/Community/UserLikeMovie.vue";

export const useAccountStore = defineStore(
  "account",
  () => {
    const API_URL = "http://127.0.0.1:8000";
    const token = ref(null);
    const userName = ref(null);
    const router = useRouter();
    // 회원 관련 ===============================================================================================

    const loginResult = ref(null);

    // 로그인
    const logIn = async function (payload) {
      const { username, password } = payload;

      try {
        const res = await axios.post(`${API_URL}/accounts/login/`, {
          username,
          password,
        });
        console.log("로그인이 완료되었습니다");
        token.value = res.data.key;
        loginResult.value = true;
        userName.value = username;
        console.log(userName.value);
      } catch (err) {
        console.log(err);
        loginResult.value = false; // 로그인 실패 상태 설정
      }
    };

    // 인증 상태 여부
    const isLogin = computed(() => {
      if (token.value === null) {
        return false;
      } else {
        return true;
      }
    });

    // 로그아웃
    const logOut = function () {
      console.log("로그아웃 전 token", token.value);
      console.log("로그아웃 전 userName", userName.value);
      token.value = null;
      userName.value = null;
      console.log("로그아웃 후 token", token.value);
      console.log("로그아웃 후 userName", userName.value);
    };

    // 회원정보 수정
    const UserUpdate = function (payload) {
      const { old_password, new_password1, new_password2 } = payload;

      axios({
        method: "post",
        url: `${API_URL}/accounts/password/change/`,
        headers: {
          Authorization: `Token ${token.value}`,
          "Content-Type": "application/json",
        },
        data: {
          old_password: old_password,
          new_password1: new_password1,
          new_password2: new_password2,
        },
      })
        .then((res) => {
          console.log(res.data);
          console.log("회원정보 수정이 완료되었습니다.");
          logOut();
          router.push({ name: "HomeView" });
        })
        .catch((err) => {
          console.log(err.response.data);
        });
    };

    // 영화 관련 ===============================================================================================

    // 검색 결과 저장
    const searchResults = ref([]);

    // 이미지 경로 반환
    const getPosterPath = (path) => {
      const TMDB_URL = "https://image.tmdb.org/t/p/w780"; // TMDB 이미지 베이스 URL
      return `${TMDB_URL}${path}`;
    };

    const getBackDrop = (path) => {
      const TMDB_URL = "https://image.tmdb.org/t/p/original";
      return `${TMDB_URL}${path}`;
    };

    const getOttPath = (path) => {
      const TMDB_URL = "https://image.tmdb.org/t/p/w200";
      return `${TMDB_URL}${path}`;
    };

    // return { signUp, errorMessage, logIn, token, API_URL, getPosterPath, searchResults  };
    return {
      logIn,
      token,
      API_URL,
      getPosterPath,
      searchResults,
      token,
      isLogin,
      loginResult,
      logOut,
      userName,
      getBackDrop,
      getOttPath,
      UserUpdate,
    };
  },
  { persist: true }
);
