<template>
  <div class="container my-3">
    <div class="page-title mb-5">
      <h1>전체 영화 조회</h1>
    </div>
    <div class="movie-list-container">
      <!-- 국가, 장르 중복체크 가능 -->
      <div class="select-option-form">
        <!-- 국가 선택 -->
        <div class="select-country">
          <h4>국가 선택</h4>

          <!-- 미국 -->
          <input
            type="checkbox"
            class="btn-check"
            id="ctr1"
            value="1"
            v-model="checkedCountry"
          />
          <label for="ctr1" class="btn">미국</label>
          <!-- 한국 -->
          <input
            type="checkbox"
            class="btn-check"
            id="ctr2"
            value="2"
            v-model="checkedCountry"
          />
          <label for="ctr2" class="btn">한국</label>
          <!-- 영국 -->
          <input
            type="checkbox"
            class="btn-check"
            id="ctr3"
            value="3"
            v-model="checkedCountry"
          />
          <label for="ctr3" class="btn">영국</label>
          <!-- 일본 -->
          <input
            type="checkbox"
            class="btn-check"
            id="ctr4"
            value="4"
            v-model="checkedCountry"
          />
          <label for="ctr4" class="btn">일본</label>
          <!-- 중국 -->
          <input
            type="checkbox"
            class="btn-check"
            id="ctr5"
            value="5"
            v-model="checkedCountry"
          />
          <label for="ctr5" class="btn">중국</label>
          <!-- 프랑스 -->
          <input
            type="checkbox"
            class="btn-check"
            id="ctr6"
            value="6"
            v-model="checkedCountry"
          />
          <label for="ctr6" class="btn">프랑스</label>
          <!-- 기타 국가 -->
          <input
            type="checkbox"
            class="btn-check"
            id="ctr7"
            value="7"
            v-model="checkedCountry"
          />
          <label for="ctr7" class="btn">기타 국가</label>
        </div>
        <!-- 장르 선택 -->
        <div class="select-genre">
          <h4>장르 선택</h4>
          <!-- 모험, 판타지 -->
          <input
            type="checkbox"
            class="btn-check"
            id="gen1"
            value="12, 14"
            @change="handleGenreChange($event)"
          />
          <label for="gen1" class="btn">🎇모험, 판타지 🎆</label>
          <!-- 로맨스-->
          <input
            type="checkbox"
            class="btn-check"
            id="gen2"
            value="10749"
            @change="handleGenreChange($event)"
          />
          <label for="gen2" class="btn">💖로맨스💝</label>
          <input
            type="checkbox"
            class="btn-check"
            id="gen3"
            value="18, 35"
            @change="handleGenreChange($event)"
          />
          <label for="gen3" class="btn">🤗드라마, 코미디🤣</label>

          <!-- 애니메이션, TV 영화  -->
          <input
            type="checkbox"
            class="btn-check"
            id="gen4"
            value="16, 10770"
            @change="handleGenreChange($event)"
          />
          <label for="gen4" class="btn">🧞‍♂️애니, tv📺</label>

          <!-- 음악, 가족 -->
          <input
            type="checkbox"
            class="btn-check"
            id="gen5"
            value="10402, 10751"
            @change="handleGenreChange($event)"
          />
          <label for="gen5" class="btn">🎵음악, 가족👨‍👩‍👧‍👦</label>
          <!-- 공포, 스릴러-->
          <input
            type="checkbox"
            class="btn-check"
            id="gen6"
            value="27, 53"
            @change="handleGenreChange($event)"
          />
          <label for="gen6" class="btn">😱공포, 스릴러🧛‍♀️</label>
          <!-- SF, 미스터리 -->
          <input
            type="checkbox"
            class="btn-check"
            id="gen7"
            value="878, 9648"
            @change="handleGenreChange($event)"
          />
          <label for="gen7" class="btn">👨‍🚀SF, 미스터리😲</label>

          <!-- 액션, 범죄 -->
          <input
            type="checkbox"
            class="btn-check"
            id="gen8"
            value="28, 80"
            @change="handleGenreChange($event)"
          />
          <label for="gen8" class="btn">🏃‍♀️액션, 범죄👮‍♂️</label>
          <!-- 역사, 다큐멘터리 -->
          <input
            type="checkbox"
            class="btn-check"
            id="gen9"
            value="36, 99"
            @change="handleGenreChange($event)"
          />
          <label for="gen9" class="btn">💫역사, 다큐멘터리📚</label>
          <!-- 서부, 전쟁 -->
          <input
            type="checkbox"
            class="btn-check"
            id="gen10"
            value="37, 10752"
            @change="handleGenreChange($event)"
          />
          <label for="gen10" class="btn">🤠서부, 전쟁🏹</label>
        </div>
        <!-- 정렬 기준 선택 -->
        <div class="select-criteria d-flex flex-row justify-content-end">
          <!-- <label for="sort">정렬 기준</label><br /> -->
          <select class="selectBox mx-2" v-model="sortOption">
            <option value="recent">최신</option>
            <option value="review">리뷰</option>
            <option value="like">좋아요</option>
            <option value="popularity">인기</option>
          </select>
          <div class="select-movies">
            <button class="listBtn mx-2" @click="loadMovies">영화 조회</button>
          </div>
        </div>
      </div>
      <div class="row movie-list mt-4 d-flex justify-content-center">
        <MovieCard
          v-for="movie in movieList"
          :key="movie.id"
          :movie="movie"
          class="movieCard col-12 col-sm-6 col-md-4 col-lg-3 mb-4"
        />
      </div>
      <Pagination
        class="d-flex justify-content-center"
        :current-page="currentPage"
        :total-pages="totalPages"
        :page-group="pageGroup"
        :group-size="groupSize"
        @page-changed="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useAccountStore } from "@/stores/accounts";
import axios from "axios";
import qs from "qs";
import MovieCard from "@/components/Movies/MovieCard.vue";
import Pagination from "@/components/Pagination.vue";

const store = useAccountStore();
const checkedCountry = ref([]);
const checkedGenre = ref([]);
const sortOption = ref("recent"); // 기본 정렬 기준

// 페이지 네이션 관련 ===================================
const currentPage = ref(1);
const totalPages = ref(1);
const pageGroup = ref(1);
const groupSize = ref(7);

// 장르 변경 핸들러
const handleGenreChange = (event) => {
  const genreValues = event.target.value.split(","); // 여러 값을 쉼표로 분리
  if (event.target.checked) {
    // 체크된 경우 배열에 추가
    checkedGenre.value.push(...genreValues.map((value) => value.trim())); // 공백 제거
  } else {
    // 체크 해제된 경우 배열에서 제거
    checkedGenre.value = checkedGenre.value.filter(
      (item) => !genreValues.some((value) => value.trim() === item)
    );
  }
};

const movieList = ref([]);
const loadMovies = (page = 1) => {
  const params = {
    country: checkedCountry.value,
    genre: checkedGenre.value,
    sort: sortOption.value,
    page,
  };
  console.log(params);

  axios({
    method: "get",
    url: `${store.API_URL}/api/v1/movies`,
    params,
    paramsSerializer: (params) => {
      return qs.stringify(params, { arrayFormat: "repeat" });
    },
  })
    .then((res) => {
      console.log(res.data);
      movieList.value = res.data.results;
      totalPages.value = Math.ceil(res.data.count / 20);
      pageGroup.value = Math.ceil(currentPage.value / groupSize.value);
    })
    .catch((err) => {
      console.log(err);
    });
};

// 페이지 변경 핸들러
const handlePageChange = (page) => {
  if (typeof page === "number") {
    currentPage.value = page;
    loadMovies(page);
  }
};

// 초기 데이터 로드 (옵션으로 호출 가능)
onMounted(() => {
  loadMovies();
});

// 페이지가 변경될 때마다 페이직 그룹 갱신
watch(currentPage, () => {
  pageGroup.value = Math.ceil(currentPage.value / groupSize.value);
});
</script>

<style scoped>
.btn {
  margin-right: 10px;
  margin-bottom: 10px;
  border: 2px solid transparent;
  transition: border-color 0.3s;
}

.btn:last-child {
  margin-right: 0;
}
.btn-check:checked + label {
  border-color: #d2de32;
}
.listBtn {
  background-color: #febbcc;
  border: 2px solid #ffcccc;
  border-radius: 5px;
  font-size: 18px;
}
.selectBox {
  border: none;
  border-radius: 5px;

  width: 12%;
}
.selectBox:focus {
  border: #e6a4b4;
}
</style>
