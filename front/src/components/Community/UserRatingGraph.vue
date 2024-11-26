<template>
  <div class="rating-statistics my-4">
    <div v-if="isDataReady" class="chart-content">
      <h3 class="average-rating-text">평균 별점: <span class="rating-value">{{ averageRating.toFixed(2) }}</span></h3>
      <div class="chart-container">
        <canvas ref="ratingChartRef"></canvas>
      </div>
    </div>
    <div v-else class="loading">
      데이터 로딩 중...⭐
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";
import { Chart, registerables } from "chart.js";
import { useAccountStore } from "@/stores/accounts";
import ChartDataLabels from 'chartjs-plugin-datalabels';
Chart.register(ChartDataLabels);
Chart.register(...registerables);

const store = useAccountStore();
const route = useRoute();

const averageRating = ref(null);
const ratingDistribution = ref(null);
const chartInstance = ref(null);
const ratingChartRef = ref(null);

// 데이터 준비 상태 체크
const isDataReady = computed(() => {
  return averageRating.value !== null && 
         ratingDistribution.value !== null &&
         Object.keys(ratingDistribution.value).length > 0;
});

const initChart = async () => {
  if (!isDataReady.value) {
    console.log('데이터 로드 실패');
    return;
  }

  try {
    if (chartInstance.value) {
      try {
        chartInstance.value.destroy();
      } catch (error) {
        console.error('Error while destroying chart:', error);
      }
      chartInstance.value = null;
    }

    await nextTick();

    const canvas = ratingChartRef.value;
    if (!canvas) {
      console.error('Canvas element not found');
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.error('Canvas context not found');
      return;
    }

    const data = Object.entries(ratingDistribution.value)
      .filter(([key, value]) => !isNaN(parseFloat(key)) && !isNaN(value))
      .map(([key, value]) => ({
        rating: parseFloat(key),
        count: parseInt(value, 10),
      }))
      .sort((a, b) => a.rating - b.rating);

    if (data.length === 0) {
      console.error('No valid data points');
      return;
    }

    chartInstance.value = new Chart(ctx, {
  type: 'line',
  data: {
    labels: data.map((item) => `${item.rating.toFixed(1)}`),
    datasets: [
      {
        label: '별점 추이',
        data: data.map((item) => item.count),
        borderColor: '#fba1b7',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderWidth: 4,
        pointBackgroundColor: '#fba1b7',
        pointRadius: 8,
        pointHoverRadius: 7,
        fill: false,
        tension: 0.4,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false, // 차트 크기 조정 가능
    animation: { duration: 0 },
    layout: {
      padding: {
        top: 50, // 그래프 상단 여백
      },
    },
    plugins: {
      legend: {
        display: false, // 범례 숨김
      },
      tooltip: {
        enabled: true,
        callbacks: {
          label: (context) => `${context.parsed.y}개`,
        },
      },
      datalabels: {
        display: false, // 포인트 위 수치 출력 비활성화
      },
    },
    scales: {
      y: {
        display: false, // 세로축 숨김
        suggestedMax: Math.max(...data.map((item) => item.count)) + 2, // 상단 여유 공간 추가
      },
      x: {
        title: {
          display: true,
        },
        ticks: {
          color: 'rgba(100, 100, 100, 1)',
        },
        grid: {
          drawBorder: true,
          drawOnChartArea: false,
        },
      },
    },
  },
  plugins: {
    afterDatasetsDraw: (chart) => {
      const ctx = chart.ctx;
      const dataset = chart.data.datasets[0];
      const meta = chart.getDatasetMeta(0);

      if (!dataset || !meta) return;

      // 최대값 찾기
      const maxValue = Math.max(...dataset.data);
      const maxIndex = dataset.data.findIndex((value) => value === maxValue);
      const x = meta.data[maxIndex].x; // x 좌표
      const y = meta.data[maxIndex].y; // y 좌표

      // ⭐ 표시
      ctx.save();
      ctx.font = '20px Arial'; // 이모지 크기 조절
      ctx.textAlign = 'center';
      ctx.fillStyle = 'rgba(255, 193, 7, 1)'; // 노란색
      ctx.fillText('⭐', x, y - 10); // 점 위에 표시
      ctx.restore();
    },
  },
});





    console.log('Chart created successfully');
  } catch (error) {
    console.error('Chart creation error:', error);
  }
};





const fetchReviewGraph = async (username) => {
  try {
    const response = await axios.get(
      `${store.API_URL}/api/v1/user-page/${username}/review-graph/`
    );
    
    if (response.data) {
      averageRating.value = response.data.average_rating;
      ratingDistribution.value = response.data.rating_distribution;
      
      console.log('Data fetched:', {
        averageRating: averageRating.value,
        ratingDistribution: ratingDistribution.value
      });
      
      // 데이터 로드 후 차트 초기화
      await initChart();
    }
  } catch (error) {
    console.error("Data fetch error:", error);
  }
};

// 컴포넌트 마운트 시 데이터 로드
onMounted(async () => {
  console.log('Component mounted');
  const username = route.params.username;
  if (username) {
    await fetchReviewGraph(username);
    await nextTick(); // DOM 렌더링 보장
    await initChart();
  }
});

// 데이터 변경 감지
watch(isDataReady, async (newValue) => {
  console.log('Data ready changed:', newValue);
  if (newValue) {
    await nextTick();
    await initChart();
  }
});
</script>

<style scoped>
.rating-statistics {
  width: 100%;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9; /* 배경을 부드러운 색으로 */
  border-radius: 10px; /* 모서리를 둥글게 */
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 약간의 그림자 */
}

.chart-content {
  width: 90%;
  padding: 20px;
  background-color: #ffffff; /* 배경 흰색 */
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center; /* 텍스트 가운데 정렬 */
}

.average-rating-text {
  font-size: 18px; /* 텍스트 크기 줄이기 */
  font-weight: bold; /* 텍스트 강조 */
  color: #444; /* 중간 톤 색상 */
  margin-bottom: 15px; /* 아래쪽 여백 추가 */
}

.rating-value {
  font-size: 22px; /* 별점 값 크기를 강조 */
  color: #666; /* 별점 값을 강조하는 색상 */
}


.chart-container {
  position: relative;
  height: 300px; /* 명확한 높이 */
  width: 100%;
  margin-top: 20px; /* 상단 여백 */
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 18px; /* 텍스트 크기 조정 */
  font-weight: bold; /* 텍스트 강조 */
}

/* 차트 내부 요소 스타일 */
canvas {
  border-radius: 10px; /* 캔버스 모서리 둥글게 */
}
</style>
