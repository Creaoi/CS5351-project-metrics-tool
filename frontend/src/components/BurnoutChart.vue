<template>
  <div class="table-container">
    <a-card class="dashboard-card shadow-md rounded-2xl">
      <a-typography>
        <div class="header-bar">
          <a-typography-title level="2" class="text-center">
            Sprint Burnout Chart
          </a-typography-title>
          <a-button type="primary" @click="reloadData" ghost>🔄 Refresh Data</a-button>
        </div>
        <a-divider />

        <!-- 进度概览 -->
        <div class="progress-container">
          <div class="progress-item" v-for="item in progressItems" :key="item.label">
            <p class="font-semibold">{{ item.label }}</p>
            <a-progress
              type="circle"
              :percent="item.percent"
              :format="() => item.value"
              :status="item.status"
            />
          </div>
        </div>

        <!-- 折线图展示 -->
        <div class="chart-container">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </a-typography>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const burnoutData = ref([]);
const idealData = ref([]);
const startPoints = ref(0);
const currentPoints = ref(0);
const chartCanvas = ref(null);
let chartInstance = null;

// 动态计算完成数与百分比
const completedPoints = computed(() => startPoints.value - currentPoints.value);
const progressPercent = computed(() =>
  startPoints.value ? (currentPoints.value / startPoints.value) * 100 : 0
);

const progressItems = computed(() => [
  { label: "Initial Points", value: startPoints.value, percent: 100, status: "" },
  { label: "Remaining", value: currentPoints.value, percent: progressPercent.value, status: "active" },
  { label: "Completed", value: completedPoints.value, percent: 100 - progressPercent.value, status: "success" },
]);

// ✅ 封装加载数据函数
const loadData = async () => {
  const response = await fetch("/burnout.json");
  const json = await response.json();
  burnoutData.value = json.actual;

  if (burnoutData.value.length > 0) {
    startPoints.value = burnoutData.value[0].remaining_points;
    currentPoints.value = burnoutData.value.at(-1).remaining_points;

    // 生成理想线数据（线性下降）
    const totalDays = burnoutData.value.length - 1;
    idealData.value = burnoutData.value.map((d, i) => ({
      date: d.date,
      remaining_points: startPoints.value - (startPoints.value / totalDays) * i,
    }));
  }

  drawChart();
};

// ✅ 重新加载数据
const reloadData = () => {
  if (chartInstance) {
    chartInstance.destroy();
  }
  loadData();
};

// ✅ 绘制图表
const drawChart = () => {
  const ctx = chartCanvas.value.getContext("2d");

  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, "rgba(64, 158, 255, 0.25)");
  gradient.addColorStop(1, "rgba(64, 158, 255, 0)");

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: burnoutData.value.map((d) => d.date),
      datasets: [
        {
          label: "Actual Progress",
          data: burnoutData.value.map((d) => d.remaining_points),
          borderColor: "#409EFF",
          backgroundColor: gradient,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: "#409EFF",
          pointHoverRadius: 8,
          borderWidth: 2,
        },
        {
          label: "Ideal Line",
          data: idealData.value.map((d) => d.remaining_points),
          borderColor: "#ff7c6b",
          borderDash: [8, 4],
          fill: false,
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 1000,
        easing: "easeOutQuart",
      },
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#555" },
        },
        tooltip: {
          backgroundColor: "rgba(0,0,0,0.75)",
          titleFont: { size: 14 },
          bodyFont: { size: 13 },
          callbacks: {
            label: (ctx) => `Remaining: ${ctx.parsed.y.toFixed(1)} pts`,
          },
        },
      },
      scales: {
        x: {
          ticks: { color: "#666" },
          grid: { display: false },
        },
        y: {
          beginAtZero: true,
          ticks: { color: "#666" },
          grid: {
            color: "rgba(0,0,0,0.05)",
          },
        },
      },
    },
  });
};

onMounted(loadData);
</script>

<style scoped>
.table-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-card {
  padding: 20px;
  background: linear-gradient(180deg, #f8faff 0%, #ffffff 100%);
}

/* 顶部标题栏 */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* ---------- 进度条容器 ---------- */
.progress-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 40px;
  margin-bottom: 30px;
}
.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 120px;
}

/* ---------- 折线图容器 ---------- */
.chart-container {
  width: 100%;
  height: 320px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  padding: 10px 0;
}

canvas {
  max-width: 100%;
}

@media (max-width: 640px) {
  .progress-item {
    width: 100px;
    margin-bottom: 20px;
  }
  .progress-container {
    gap: 20px;
  }
}
</style>
