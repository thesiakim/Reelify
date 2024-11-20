<template>
  <div class="container">
    <div class="page-title">
      <h1>전체 영화 조회</h1>
    </div>
    <!-- 국가, 장르 중복체크 가능 -->
    <div class="select-option-form">
      <!-- 국가 선택 -->
      <div class="select-country">
        <div>국가 : {{ checkedCountry }}</div>

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
          value="Other"
          v-model="checkedCountry"
        />
        <label for="ctr7" class="btn">기타 국가</label>
      </div>
      <!-- 장르 선택 -->
      <div class="select-genre">
        <div>장르 : {{ checkedGenre }}</div>

        <!-- 모험, 판타지, sf, 액션 -->
        <input
          type="checkbox"
          class="btn-check"
          id="gen1"
          value="12, 14, 878, 28"
          @change="handleGenreChange($event)"
        />
        <label for="gen1" class="btn">모, 판, s, 액</label>
        <!-- 드라마, 로맨스, 음악 -->
        <input
          type="checkbox"
          class="btn-check"
          id="gen2"
          value="18, 10749, 10402"
          @change="handleGenreChange($event)"
        />
        <label for="gen2" class="btn">드, 로, 음</label>
        <!-- 애니메이션, TV 영화  -->
        <input
          type="checkbox"
          class="btn-check"
          id="gen3"
          value="16, 10770"
          @change="handleGenreChange($event)"
        />
        <label for="gen3" class="btn">애니, tv</label>
        <!-- 코미디, 가족 -->
        <input
          type="checkbox"
          class="btn-check"
          id="gen4"
          value="35, 10751"
          @change="handleGenreChange($event)"
        />
        <label for="gen4" class="btn">코, 가</label>
        <!-- 역사, 다큐멘터리, 전쟁 -->
        <input
          type="checkbox"
          class="btn-check"
          id="gen5"
          value="36, 99, 10752"
          @change="handleGenreChange($event)"
        />
        <label for="gen5" class="btn">역, 다, 전</label>
        <!-- 서부, 스릴러, 범죄, 미스터리 -->
        <input
          type="checkbox"
          class="btn-check"
          id="gen6"
          value="37, 53, 80, 9648"
          @change="handleGenreChange($event)"
        />
        <label for="gen6" class="btn">서부, 스릴러, 범죄, 미스터리</label>
      </div>
      <!-- 정렬 기준 선택 -->
      <div class="select-criteria">
        <label for="sort">정렬 기준</label><br />
        <select v-model="sortOption">
          <option value="recent">최신</option>
          <option value="review">리뷰</option>
          <option value="like">좋아요</option>
          <option value="popularity">인기</option>
        </select>
      </div>
      <div class="select-movies">
        <button @click="loadMovies">영화 조회</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAccountStore } from "@/stores/accounts";
import axios from "axios";
import qs from "qs";

const store = useAccountStore();
const checkedCountry = ref([]);
const checkedGenre = ref([]);
const sortOption = ref("recent"); // 기본 정렬 기준

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

const loadMovies = () => {
  const params = {
    country: checkedCountry.value,
    genre: checkedGenre.value,
    sort: sortOption.value,
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
    })
    .catch((err) => {
      console.log(err);
    });
};

// 초기 데이터 로드 (옵션으로 호출 가능)
onMounted(() => {
  loadMovies();
});
</script>

<style scoped></style>
