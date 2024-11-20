<template>
  <div>
    <div id="carouselExampleCaptions" class="carousel slide">
      <div class="carousel-indicators">
        <button
          type="button"
          data-bs-target="#carouselExampleCaptions"
          data-bs-slide-to="0"
          class="active"
          aria-current="true"
          aria-label="Slide 1"
        ></button>
        <button
          type="button"
          data-bs-target="#carouselExampleCaptions"
          data-bs-slide-to="1"
          aria-label="Slide 2"
        ></button>
        <button
          type="button"
          data-bs-target="#carouselExampleCaptions"
          data-bs-slide-to="2"
          aria-label="Slide 3"
        ></button>
      </div>
      <div class="carousel-inner">
        <div class="carousel-item active">
          <img
            src="@/assets/Home/carouselImg1.jpg"
            class="d-block w-100 carouselImg"
            alt="carouselImg1"
          />
          <div class="carousel-caption d-none d-md-block">
            <h3 class="home-title">Reelify</h3>
            <p class="home-content">영화에 대한 생각을 나누는 공간</p>
          </div>
        </div>
        <div class="carousel-item">
          <img
            src="@/assets/Home/carouselImg2.jpg"
            class="d-block w-100 carouselImg"
            alt="carouselImg2"
          />
          <div class="carousel-caption d-none d-md-block">
            <h3 class="home-title">Reelify</h3>
            <p class="home-content">사람들과 함께</p>
          </div>
        </div>
        <div class="carousel-item">
          <img
            src="@/assets/Home/carouselImg3.jpeg"
            class="d-block w-100 carouselImg"
            alt="carouselImg3"
          />
          <div class="carousel-caption d-none d-md-block">
            <h5 class="home-title">Reelify</h5>
            <p class="home-content">지금 여기서</p>
          </div>
        </div>
      </div>
      <button
        class="carousel-control-prev"
        type="button"
        data-bs-target="#carouselExampleCaptions"
        data-bs-slide="prev"
      >
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Previous</span>
      </button>
      <button
        class="carousel-control-next"
        type="button"
        data-bs-target="#carouselExampleCaptions"
        data-bs-slide="next"
      >
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Next</span>
      </button>
    </div>
    <div v-if="store.isLogin === false" class="mt-4 text-center">
      <h2>지금 여기서 나눠보세요</h2>
      <RouterLink class="routerlink gradient-text" :to="{ name: 'SignUpView' }"
        >Reelify 회원 되기</RouterLink
      >
    </div>
    <div v-if="store.isLogin === true" class="mt-4 text-center">
      <div class="welcome-container">
        <h2>환영합니다.</h2>
        <h2 class="gradient-name">{{ store.userName }}님</h2>
      </div>
      <RouterLink
        class="routerlink gradient-text"
        :to="{ name: 'MovieListView' }"
        >Reelify 하러 가기</RouterLink
      >
    </div>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
import { useAccountStore } from "@/stores/accounts";

const store = useAccountStore();
</script>

<style scoped>
.carouselImg {
  height: 80vh;
  width: 100vw;
}
.carousel-inner {
  height: 100%;
}
.home-title {
  font-weight: bold;
}
.home-content {
  font-weight: bold;
}
.routerlink {
  text-decoration: none;
  color: #a1eebd;
}
.welcome-container {
  justify-content: center;
  display: flex;
  align-items: center;
  gap: 10px;
}

.gradient-text {
  background: linear-gradient(90deg, #ffccea, #a1eebd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: bold; /* 텍스트 강조 (선택사항) */
  font-size: 1.5rem; /* 텍스트 크기 조정 (선택사항) */
}

.gradient-name {
  background: linear-gradient(90deg, #a1eebd, #ffccea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: bold; /* 텍스트 강조 (선택사항) */ /* 텍스트 크기 조정 (선택사항) */
}
</style>
