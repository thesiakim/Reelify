<script setup>
import { ref, onMounted } from "vue";
import MovieMapDetail from "@/components/Movies/MovieMapDetail.vue";

const API_KEY = import.meta.env.VITE_KAKAO_API_KEY;
const JS_KEY = import.meta.env.VITE_KAKAO_JS_KEY;

const mapContainer = ref(null);
let mapInstance = null;
const theaters = ref([]);
const addedPlaces = new Set();

const SEARCH_RADIUS = 2000; // 검색 반경 (2km)
const INITIAL_LEVEL = 3; // 초기 지도 레벨

const loadKakaoMap = async () => {
  const script = document.createElement("script");
  script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${JS_KEY}&autoload=false`;
  document.head.append(script);

  script.onload = async () => {
    window.kakao.maps.load(async () => {
      const options = {
        center: new window.kakao.maps.LatLng(33.450701, 126.570667),
        level: INITIAL_LEVEL,
      };
      mapInstance = new window.kakao.maps.Map(mapContainer.value, options);

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const latitude = position.coords.latitude;
          const longitude = position.coords.longitude;

          const currentLocation = new window.kakao.maps.LatLng(
            latitude,
            longitude
          );
          mapInstance.setCenter(currentLocation);

          // 현재 위치 마커 추가
          addMarker(mapInstance, latitude, longitude, "현재 위치", true);

          // 현재 위치 기준 영화관 검색 및 표시
          const movieTheaters = await fetchMovieTheaters(latitude, longitude);
          theaters.value = movieTheaters;
          addTheaterMarkers(mapInstance, movieTheaters);

          // 지도 범위 조정
          adjustMapBounds(mapInstance, movieTheaters, latitude, longitude);

          // 지도 이벤트 리스너 추가
          addMapEventListeners(mapInstance);
        },
        (error) => {
          console.error("위치 정보를 가져올 수 없습니다.", error);
        }
      );
    });
  };
};

const fetchMovieTheaters = async (latitude, longitude) => {
  try {
    const url = `https://dapi.kakao.com/v2/local/search/keyword.json?query=영화관&x=${longitude}&y=${latitude}&radius=${SEARCH_RADIUS}`;
    const response = await fetch(url, {
      headers: { Authorization: `KakaoAK ${API_KEY}` },
    });

    if (!response.ok) {
      throw new Error(`API 요청 실패: ${response.status}`);
    }

    const data = await response.json();

    return data.documents.filter((theater) => {
      if (addedPlaces.has(theater.id)) return false;
      addedPlaces.add(theater.id);
      return true;
    });
  } catch (error) {
    console.error("API 요청 중 에러 발생:", error);
    return [];
  }
};

const addMarker = (
  map,
  latitude,
  longitude,
  title,
  isCurrentLocation = false
) => {
  const position = new window.kakao.maps.LatLng(latitude, longitude);
  const markerImage = isCurrentLocation
    ? new window.kakao.maps.MarkerImage(
        "https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png",
        new window.kakao.maps.Size(24, 35),
        { offset: new window.kakao.maps.Point(12, 35) }
      )
    : null;

  new window.kakao.maps.Marker({
    position,
    map,
    image: markerImage,
    title,
  });
};

const addTheaterMarkers = (map, theaters) => {
  theaters.forEach((theater) => {
    const { y, x, place_name } = theater;
    addMarker(map, y, x, place_name);
  });
};

const adjustMapBounds = (map, theaters, latitude, longitude) => {
  const bounds = new window.kakao.maps.LatLngBounds();

  // 현재 위치 포함
  bounds.extend(new window.kakao.maps.LatLng(latitude, longitude));

  // 영화관 위치 포함
  theaters.forEach((theater) => {
    bounds.extend(new window.kakao.maps.LatLng(theater.y, theater.x));
  });

  map.setBounds(bounds);
};

const addMapEventListeners = (map) => {
  kakao.maps.event.addListener(map, "dragend", async () => {
    await handleMapEvent(map);
  });

  kakao.maps.event.addListener(map, "zoom_changed", async () => {
    await handleMapEvent(map);
  });
};

const handleMapEvent = async (map) => {
  const center = map.getCenter();
  const latitude = center.getLat();
  const longitude = center.getLng();

  // 새로운 영화관 검색
  const movieTheaters = await fetchMovieTheaters(latitude, longitude);
  theaters.value = [...theaters.value, ...movieTheaters]; // 기존 + 신규 영화관

  // 영화관 마커 추가
  addTheaterMarkers(map, movieTheaters);
};
onMounted(() => {
  if (mapContainer.value) {
    loadKakaoMap();
  }
});
</script>

<template>
  <div class="container">
    <h1>내 주변 영화관을 확인하세요</h1>
    <div ref="mapContainer" style="width: 100%; height: 70vh"></div>
    <MovieMapDetail :mapInstance="mapInstance" :theaters="theaters" />
  </div>
</template>
