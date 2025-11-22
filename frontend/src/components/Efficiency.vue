<template>
  <div class="table-container">
    <a-card class="dashboard-card shadow-md rounded-2xl">
      <a-typography>
        <a-typography-title level="2" class="text-center">
          Pull Request Efficiency Dashboard
        </a-typography-title>
        <a-divider />

        <!-- 1️⃣ 整体效率统计 -->
        <div class="progress-container">
          <div class="progress-item">
            <p class="font-semibold">average efficiency score</p>
            <a-progress
              type="circle"
              :percent="efficiencyPercent"
              :format="() => overall.average_efficiency_score.toFixed(1)"
              stroke-color="#52c41a"
            />
          </div>
          <div class="progress-item">
            <p class="font-semibold">average merge time</p>
            <a-progress
              type="circle"
              :percent="mergePercent"
              :format="() => overall.average_merge_time_hours.toFixed(1) + 'h'"
              stroke-color="#1890ff"
            />
          </div>
          <div class="progress-item">
            <p class="font-semibold">average review time</p>
            <a-progress
              type="circle"
              :percent="reviewPercent"
              :format="() => overall.average_review_time_hours.toFixed(1) + 'h'"
              stroke-color="#faad14"
            />
          </div>
        </div>

        <!-- 2️⃣ PR 效率对比 -->
        <a-divider />
        <div class="chart-container">
          <canvas ref="efficiencyChart"></canvas>
        </div>

        <!-- 3️⃣ PR 详细信息 -->
        <a-divider />
        <a-typography-title level="4" class="text-center mt-4">
          PR Details
        </a-typography-title>
        <a-table
          :columns="columns"
          :data-source="prDetails"
          row-key="pr_id"
          bordered
          class="w-4/5 mx-auto mt-4"
          :pagination="{ pageSize: 5 }"
        />
      </a-typography>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { Chart, registerables } from "chart.js";
Chart.register(...registerables);

const columns = [
  { title: "PR ID", dataIndex: "pr_id", key: "pr_id" },
  { title: "create time", dataIndex: "created_at", key: "created_at" },
  { title: "merge time", dataIndex: "merged_at", key: "merged_at" },
  { title: "state", dataIndex: "state", key: "state" },
  { title: "merge duration (h)", dataIndex: "merge_time_hours", key: "merge_time_hours" },
  { title: "review duration (h)", dataIndex: "average_review_time_hours", key: "average_review_time_hours" },
  { title: "total changes", dataIndex: "total_changes", key: "total_changes" },
  { title: "efficiency score", dataIndex: "efficiency_score", key: "efficiency_score" },
];

const overall = ref({
  average_efficiency_score: 0,
  average_merge_time_hours: 0,
  average_review_time_hours: 0,
});
const prDetails = ref([]);
const efficiencyChart = ref(null);

const efficiencyPercent = computed(() => Math.min((overall.value.average_efficiency_score / 100000) * 100, 100));
const mergePercent = computed(() => Math.min((overall.value.average_merge_time_hours / 100) * 100, 100));
const reviewPercent = computed(() => Math.min((overall.value.average_review_time_hours / 100) * 100, 100));

onMounted(async () => {
  const res = await fetch("/calculate_pr_review_efficiency.json");
  const data = await res.json();

  overall.value = data.overall_statistics;
  prDetails.value = data.pr_details;

  const ctx = efficiencyChart.value.getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: prDetails.value.map((pr) => "PR #" + pr.pr_id),
      datasets: [
        {
          label: "efficiency score",
          data: prDetails.value.map((pr) => pr.efficiency_score),
          backgroundColor: "#52c41a",
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
});
</script>

<style scoped>
@import "./DashboardStyle.css";
</style>
