<template>
  <div class="table-container" :class="{ dark: darkMode }">
    <a-card class="dashboard-card shadow-md rounded-2xl fade-in">
      <div class="header-actions">
        <a-select v-model:value="sortKey" style="width: 220px">
          <a-select-option value="total_contributions">Sort by Total Contributions</a-select-option>
          <a-select-option value="closed_issues">Sort by Closed Issues</a-select-option>
          <a-select-option value="comments">Sort by Comments</a-select-option>
        </a-select>
        <a-switch v-model:checked="darkMode" checked-children="🌙" un-checked-children="☀️" />
      </div>

      <a-typography>
        <a-typography-title level="2" class="text-center gradient-text">
          Contributor Activity Overview
        </a-typography-title>
        <a-divider />

        <!-- 📊 进度概览 -->
        <div class="progress-container">
          <div class="progress-item">
            <p class="font-semibold">Top Contributor</p>
            <a-progress
              type="circle"
              :percent="topPercent"
              :format="() => topUser"
              stroke-color="#fa8c16"
              status="active"
            />
          </div>
          <div class="progress-item">
            <p class="font-semibold">Total Contributors</p>
            <a-progress
              type="circle"
              :percent="100"
              :format="() => totalContributors"
              stroke-color="#1890ff"
              status="active"
            />
          </div>
        </div>

        <!-- 💡 数据洞察 -->
        <div class="insight-card">
          <p>💡 <b>{{ topUser }}</b> made the most contributions with <b>{{ maxContrib }}</b> total actions.</p>
          <p>📈 Average contributions: {{ avgContrib }} per contributor.</p>
        </div>

        <!-- 📈 图表区 -->
        <div class="chart-section">
          <div class="chart-box hover-up">
            <h3 class="chart-title">Contributor Activity</h3>
            <canvas ref="activityChart"></canvas>
          </div>

          <div class="chart-box hover-up">
            <h3 class="chart-title">Number of Closed Issues</h3>
            <canvas ref="closedChart"></canvas>
          </div>
        </div>

        <a-divider />

        <!-- 🧾 表格 -->
        <div class="table-wrapper">
          <h3 class="text-lg font-semibold text-center mb-3">Contributor Details</h3>
          <a-table
            :columns="columns"
            :data-source="issues"
            row-key="user"
            bordered
            class="w-full rounded-lg shadow-sm"
            :pagination="{ pageSize: 5 }"
          />
        </div>
      </a-typography>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { Chart, registerables } from "chart.js";
import { message } from "ant-design-vue";

Chart.register(...registerables);

const columns = [
  { title: "User", dataIndex: "user", key: "user" },
  { title: "Closed Issues", dataIndex: "closed_issues", key: "closed_issues" },
  { title: "Comments", dataIndex: "comments", key: "comments" },
  { title: "Total Contributions", dataIndex: "total_contributions", key: "total_contributions" },
];

const issues = ref([]);
const activityChart = ref(null);
const closedChart = ref(null);

const topUser = ref("-");
const totalContributors = ref(0);
const topPercent = ref(100);
const sortKey = ref("total_contributions");
const darkMode = ref(false);

const maxContrib = computed(() => Math.max(...issues.value.map((d) => d.total_contributions || 0)));
const avgContrib = computed(() =>
  Math.round(
    issues.value.reduce((a, b) => a + (b.total_contributions || 0), 0) / (issues.value.length || 1)
  )
);

let actChart = null;
let closeChart = null;

onMounted(async () => {
  const res = await fetch("/calculate_contributor_activity.json");
  const data = await res.json();
  issues.value = data;
  totalContributors.value = data.length;

  updateTopContributor();
  renderCharts();
});

const updateTopContributor = () => {
  const maxContribValue = Math.max(...issues.value.map((d) => d.total_contributions));
  const top = issues.value.find((d) => d.total_contributions === maxContribValue);
  topUser.value = top ? top.user : "-";
};

// 重新渲染图表（排序或主题变化时）
const renderCharts = () => {
  const data = issues.value;
  if (!data.length) return;

  if (actChart) actChart.destroy();
  if (closeChart) closeChart.destroy();

  const actCtx = activityChart.value.getContext("2d");
  const closedCtx = closedChart.value.getContext("2d");

  const gradient1 = actCtx.createLinearGradient(0, 0, 0, 400);
  gradient1.addColorStop(0, "rgba(24, 144, 255, 0.8)");
  gradient1.addColorStop(1, "rgba(24, 144, 255, 0.2)");

  const gradient2 = closedCtx.createLinearGradient(0, 0, 0, 400);
  gradient2.addColorStop(0, "rgba(82, 196, 26, 0.8)");
  gradient2.addColorStop(1, "rgba(82, 196, 26, 0.2)");

  actChart = new Chart(actCtx, {
    type: "bar",
    data: {
      labels: data.map((d) => d.user),
      datasets: [
        {
          label: "Total Contributions",
          data: data.map((d) => d.total_contributions),
          backgroundColor: gradient1,
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } },
      onClick: (_, elements) => {
        if (elements.length > 0) {
          const i = elements[0].index;
          const user = data[i];
          message.info(
            `👤 ${user.user}: ${user.total_contributions} total contributions, ${user.closed_issues} closed issues.`
          );
        }
      },
    },
  });

  closeChart = new Chart(closedCtx, {
    type: "bar",
    data: {
      labels: data.map((d) => d.user),
      datasets: [
        {
          label: "Closed Issues",
          data: data.map((d) => d.closed_issues),
          backgroundColor: gradient2,
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } },
    },
  });
};

watch(sortKey, (key) => {
  issues.value.sort((a, b) => b[key] - a[key]);
  updateTopContributor();
  renderCharts();
});

watch(darkMode, () => renderCharts());
</script>

<style scoped>
.table-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  transition: all 0.3s ease;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.dashboard-card {
  padding: 20px;
  background: linear-gradient(180deg, #f8faff 0%, #ffffff 100%);
  transition: all 0.3s ease;
}

.dark .dashboard-card {
  background: #1e293b;
  color: #e2e8f0;
}

.gradient-text {
  background: linear-gradient(90deg, #1890ff, #722ed1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.fade-in {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeUp 0.6s forwards;
}
@keyframes fadeUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ---------- 圆形进度 ---------- */
.progress-container {
  display: flex;
  justify-content: center;
  gap: 40px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}
.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 150px;
}

/* ---------- 图表 ---------- */
.chart-section {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 30px;
  margin-bottom: 30px;
}
.chart-box {
  width: 380px;
  height: 300px;
  background: #fff;
  border-radius: 16px;
  padding: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}
.hover-up:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

/* ---------- 洞察卡片 ---------- */
.insight-card {
  background: rgba(24, 144, 255, 0.05);
  border: 1px solid rgba(24, 144, 255, 0.15);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 30px;
  text-align: center;
  font-size: 15px;
  line-height: 1.6;
}

/* ---------- 暗色模式 ---------- */
.dark .chart-box {
  background: #24324a;
  color: #e2e8f0;
}
.dark .insight-card {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.15);
}
</style>
