<script setup>
import { watch } from "vue";

const props = defineProps({
  mapInstance: Object,
  theaters: Array,
});

const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c * 1000;
};

const addMarkersToMap = (map, theaters) => {
  theaters.forEach((theater) => {
    const position = new window.kakao.maps.LatLng(
      parseFloat(theater.y),
      parseFloat(theater.x)
    );

    const marker = new window.kakao.maps.Marker({
      position: position,
      map: map,
    });

    const searchUrl = `https://search.naver.com/search.naver?query=${encodeURIComponent(
      theater.place_name
    )} 영화 상영시간표`;

    const infoWindowContent = `
      <div style="
        overflow: hidden;
        box-shadow: none;
        border: none;
        width: 250px;
        color: #333;">
        <div class="map-title" style="background-color: #FFC0D9; color: white; padding: 10px; text-align: center;">
          ${theater.place_name}
        </div>
        <div style="padding: 10px; font-size: 13px;">
          <p><strong>주소:</strong> ${theater.address_name}</p>
          <p><strong>도로명 주소:</strong> ${theater.road_address_name}</p>
          <p><strong>전화번호:</strong> ${theater.phone || "정보 없음"}</p>
          <div style="text-align: center; margin-top: 10px;">
            <a href="${searchUrl}" target="_blank" style="
              display: inline-block;
              background-color: #FFC0D9;
              color: white;
              text-decoration: none;
              padding: 8px 12px;
              border-radius: 5px;">
              상영시간표 보기
            </a>
          </div>
        </div>
      </div>
    `;

    const infoWindow = new window.kakao.maps.InfoWindow({
      content: infoWindowContent,
    });

    let isOpen = false;
    window.kakao.maps.event.addListener(marker, "click", () => {
      if (isOpen) {
        infoWindow.close();
      } else {
        infoWindow.open(map, marker);
      }
      isOpen = !isOpen;
    });
  });
};

watch(
  () => props.theaters,
  (newTheaters) => {
    if (props.mapInstance) {
      addMarkersToMap(props.mapInstance, newTheaters);
    }
  }
);
</script>

<template>
  <div class="map-container">
    <!-- 마커와 관련된 정보만 처리 -->
  </div>
</template>

<style scoped></style>
