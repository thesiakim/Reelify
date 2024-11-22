<script setup>
import LoginFormModal from "./components/Accounts/LoginFormModal.vue";
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter, RouterLink, RouterView } from "vue-router";
import axios from "axios";
import { useAccountStore } from "./stores/accounts";
import { debounce } from "lodash";

const route = useRoute();
const router = useRouter();
const isHome = computed(() => route.name === "HomeView");
const isDetail = computed(() => route.name === "MovieDetailView");

const isNavExpanded = ref(true);

const toggleNav = () => {
  isNavExpanded.value = !isNavExpanded.value;
};

const showModal = ref(false);

const moveLoginFormModal = function () {
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

// navbar 설정
onMounted(() => {
  // Bootstrap Modal 초기화
  const modalElement = document.getElementById("loginModal");
  if (modalElement) {
    const modalInstance = new bootstrap.Modal(modalElement, {
      keyboard: false,
      backdrop: "static",
    });

    if (showModal.value) {
      modalInstance.show();
    } else {
      modalInstance.hide();
    }
  }
});
// 라우트에 따라 navbar의 position을 다르게 설정
const navbarPositionClass = computed(() => {
  if (route.name === "HomeView" || route.name === "MovieDetailView") {
    return "navbar-absolute";
  } else {
    return "navbar-relative";
  }
});

// 영화 검색
const query = ref(null);
const autocompleteResults = ref([]); // 자동완성 결과 저장
const store = useAccountStore();
const API_URL = store.API_URL;
const searchResults = ref([]);

const fetchAutocomplete = debounce(() => {
  if (!query.value || query.value.trim() === "") {
    autocompleteResults.value = [];
    return;
  }

  axios({
    method: "get",
    url: `${API_URL}/api/v1/movies/autocomplete/`,
    params: { query: query.value },
  })
    .then((response) => {
      console.log("API 응답 데이터:", response.data); 
      autocompleteResults.value = response.data; 
      console.log("드롭다운 데이터:", autocompleteResults.value); 
    })
    .catch((error) => {
      console.error("자동완성 API 호출 중 오류:", error);
    });
}, 200);  // 디바운스 적용

const handleInput = (event) => {
  query.value = event.target.value;
  fetchAutocomplete(); // 디바운스된 함수 호출
};

const selectAutocomplete = (title) => {
  query.value = title; // 검색창에 선택된 제목 반영
  autocompleteResults.value = []; // 자동완성 목록 닫기
};

const searchMovie = function () {
  if (!query.value || query.value.trim() === "") {
    alert("검색어를 입력해주세요.");
    return;
  }

  axios({
    method: "get",
    url: `${API_URL}/api/v1/movies/search/?query=${query.value}`,
  })
    .then((response) => {
      searchResults.value = response.data.results; // 검색 결과 저장
      store.searchResults = searchResults.value;

      console.log(searchResults.value);
      // console.log(searchResults.value);

      router.push({
        name: "MovieSearchView",
        params: { movieName: query.value },
      });
      query.value = "";
    })
    .catch((error) => {
      console.error("검색 중 에러 발생:", error);
    });
};

const activeIndex = ref(-1); // 활성화된 드롭다운 항목의 인덱스

const handleKeydown = (event) => {
  if (!autocompleteResults.value.length) return;

  if (event.key === "ArrowDown") {
    // 아래로 이동
    activeIndex.value = (activeIndex.value + 1) % autocompleteResults.value.length;
    event.preventDefault();
  } else if (event.key === "ArrowUp") {
    // 위로 이동
    activeIndex.value =
      (activeIndex.value - 1 + autocompleteResults.value.length) %
      autocompleteResults.value.length;
    event.preventDefault();
  } else if (event.key === "Enter") {
    // 엔터키로 선택
    if (activeIndex.value >= 0) {
      const selectedMovie = autocompleteResults.value[activeIndex.value];
      selectAutocomplete(selectedMovie.title); // 선택한 제목 검색창에 반영
      activeIndex.value = -1; // 인덱스 초기화
      event.preventDefault();
    }
  } else if (event.key === "Escape") {
    // ESC로 드롭다운 닫기
    autocompleteResults.value = [];
    activeIndex.value = -1;
  }
};


// 로그아웃
const logOut = function () {
  console.log("로그아웃 되었습니다.");
  store.logOut();
};
</script>

<template>
  <header>
    <div class="wrapper">
      <nav
        :class="[
          'navbar',
          'navbar-expand-lg',
          navbarPositionClass,
          isHome || isDetail
            ? 'bg-transparent text-light'
            : 'bg-transparent text-dark',
        ]"
      >
        <div class="container-fluid">
          <RouterLink class="navbar-brand" :to="{ name: 'HomeView' }"
            >Reelify</RouterLink
          >
          <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarSupportedContent"
            @click="toggleNav"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item">
                <RouterLink
                  class="routerlink"
                  :to="{ name: 'MovieListView' }"
                  :class="{
                    'text-light': isHome || isDetail,
                    'text-dark': !isHome && !isDetail,
                  }"
                  >영화</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink
                  class="routerlink"
                  :class="{
                    'text-light': isHome || isDetail,
                    'text-dark': !isHome && !isDetail,
                  }"
                  :to="{ name: 'MovieLegendaryView' }"
                  >명예의 전당</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink
                  class="routerlink"
                  :class="{
                    'text-light': isHome || isDetail,
                    'text-dark': !isHome && !isDetail,
                  }"
                  :to="{ name: 'MovieMapView' }"
                  >주변 영화관</RouterLink
                >
              </li>
              <li class="nav-item">
                <RouterLink
                  class="routerlink"
                  :class="{
                    'text-light': isHome || isDetail,
                    'text-dark': !isHome && !isDetail,
                  }"
                  :to="{ name: 'MovieRecommendedView' }"
                  >추천 영화</RouterLink
                >
              </li>
            </ul>
            <form
              @submit.prevent="searchMovie"
              v-show="isNavExpanded"
              class="d-flex position-relative"
              role="search"
            >
              <input
                class="form-control me-2"
                type="text"
                placeholder="어떤 영화가 궁금하세요?"
                aria-label="Search"
                v-model="query"
                @input="handleInput"
                @keydown="handleKeydown" 
              />
              <button class="btn search-btn">Search</button>

              <!-- 자동완성 결과 -->
              <ul
                v-if="autocompleteResults.length > 0"
                class="list-group position-absolute w-100"
                style="top: 100%; z-index: 1000;"
              >
                <li
                  v-for="(result, index) in autocompleteResults"
                  :key="result.id"
                  class="list-group-item list-group-item-action"
                  :class="{ 'active': index === activeIndex }" 
                  @click="selectAutocomplete(result.title)"
                >
                  {{ result.title }}
                </li>
              </ul>
            </form>



            <RouterLink
              v-if="store.isLogin === false"
              class="d-flex routerlink nav-item"
              :to="{ name: 'SignUpView' }"
              :class="{
                'text-light': isHome || isDetail,
                'text-dark': !isHome && !isDetail,
              }"
              >회원가입</RouterLink
            >
            <p
              v-if="store.isLogin === false"
              @click="moveLoginFormModal"
              class="d-flex routerlink nav-item relLog"
              :class="{
                'text-light': isHome || isDetail,
                'text-dark': !isHome && !isDetail,
              }"
            >
              로그인
            </p>

            <LoginFormModal
              v-if="showModal"
              @close="closeModal"
              class="text-dark"
            />

            <RouterLink
              v-if="store.isLogin === true"
              class="d-flex routerlink nav-item"
              :to="{
                name: 'UserPageView',
                params: { username: store.userName },
              }"
              :class="{
                'text-light': isHome || isDetail,
                'text-dark': !isHome && !isDetail,
              }"
              >마이페이지</RouterLink
            >
            <p
              v-if="store.isLogin === true"
              @click="logOut"
              class="d-flex routerlink nav-item relLog"
              :class="{
                'text-light': isHome || isDetail,
                'text-dark': !isHome && !isDetail,
              }"
            >
              로그아웃
            </p>
          </div>
        </div>
      </nav>
    </div>
  </header>
  <RouterView />
</template>

<style scoped>
@font-face {
  font-family: "GowunDodum-Regular";
  src: url("https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2108@1.1/GowunDodum-Regular.woff")
    format("woff");
  font-weight: normal;
  font-style: normal;
}
.bg-transparent.text-light {
  background-color: transparent !important;
  top: 0;
  width: 100%;
  z-index: 10;
  color: white !important;
}
.bg-transparent.text-dark {
  background-color: transparent !important;
  top: 0;
  width: 100%;
  z-index: 10;
  color: black !important;
}
.navbar-toggler {
  background-color: #fba1b7;
}
.text-light {
  color: white !important;
}
.text-dark {
  color: black !important;
}
.navbar-brand {
  font-family: "GowunDodum-Regular";
  margin: 10px;
  font-weight: bold;
  font-size: xx-large;
  color: #fba1b7;
}
.nav-item {
  margin: 15px;
  text-decoration: none;
}
.routerlink {
  font-family: "GowunDodum-Regular";
  text-decoration: none;
  color: white;
}
.search-btn {
  color: #fba1b7;
}
.navbar-absolute {
  position: absolute;
}
.navbar-relative {
  position: relative;
}
.relLog {
  cursor: pointer;
}

.active {
  background-color: #f0c8d2;
  color: white;
}

</style>