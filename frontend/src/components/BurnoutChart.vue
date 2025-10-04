<template>
  <div class="table-container">   <!-- ✅ 新增容器 -->
    <a-card class="w-4/5 shadow-md rounded-2xl">
      <a-typography>
        <a-typography-title level="2" class="text-center">
          Sprint Burnout Chart
        </a-typography-title>
        <a-divider />

        <!-- 进度概览 -->
        <div class="flex justify-center items-center gap-12 w-fit mx-auto mb-6">
          <div class="text-center">
            <p class="font-semibold">Initial Points</p>
            <a-progress type="circle" :percent="100" :format="() => startPoints" />
          </div>
          <div class="text-center">
            <p class="font-semibold">Current Remaining</p>
            <a-progress
              type="circle"
              :percent="progressPercent"
              :format="() => currentPoints"
              status="active"
            />
          </div>
          <div class="text-center">
            <p class="font-semibold">Completed</p>
            <a-progress
              type="circle"
              :percent="100 - progressPercent"
              :format="() => completedPoints"
              status="success"
            />
          </div>
        </div>

        <!-- 折线图展示 -->
        <div class="flex justify-center">
          <canvas id="BurnoutChart" width="600" height="300"></canvas>
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
const startPoints = ref(0);
const currentPoints = ref(0);

const completedPoints = computed(() => startPoints.value - currentPoints.value);
const progressPercent = computed(() =>
  startPoints.value ? (currentPoints.value / startPoints.value) * 100 : 0
);

onMounted(async () => {
  const response = await fetch("/burnout.json"); // 你的 JSON
  const json = await response.json();
  burnoutData.value = json.actual;

  if (burnoutData.value.length > 0) {
    startPoints.value = burnoutData.value[0].remaining_points;
    currentPoints.value = burnoutData.value[burnoutData.value.length - 1].remaining_points;
  }

  // 绘制折线图
  const ctx = document.getElementById("BurnoutChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: burnoutData.value.map(item => item.date),
      datasets: [
        {
          label: "Remaining Points",
          data: burnoutData.value.map(item => item.remaining_points),
          borderColor: "rgba(64, 158, 255, 1)", // Ant Design 蓝
          backgroundColor: "rgba(64, 158, 255, 0.2)",
          tension: 0.3,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 5
        }
      ]
    },
    options: {
      responsive: false, // ✅ 保持固定大小，避免撑满全屏
      plugins: {
        legend: { display: true },
        tooltip: { enabled: true }
      },
      scales: {
        x: {
          title: { display: true, text: "Date" }
        },
        y: {
          title: { display: true, text: "Remaining Points" },
          beginAtZero: true
        }
      }
    }
  });
});
</script>

<style scoped>
.table-container {
  max-width: 900px;   /* 控制最大宽度，例如 900px */
  margin: 0 auto;     /* 居中 */
}
.markdown-body {
  text-align: center;
}
</style>
