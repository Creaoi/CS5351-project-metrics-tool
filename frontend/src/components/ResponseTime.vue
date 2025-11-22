<template>
  <div class="table-container">
    <a-card class="dashboard-card shadow-md rounded-2xl">
      <a-typography>
        <a-typography-title level="2" class="text-center">
          Issue Response Overview
        </a-typography-title>
        <a-divider />

        <!-- 1️⃣ 平均响应时间 -->
        <div class="progress-container">
          <div class="progress-item">
            <p class="font-semibold">average response time</p>
            <a-progress
              type="circle"
              :percent="percent"
              :format="() => averageTime + 'h'"
              status="active"
            />
          </div>
        </div>

        <!-- 2️⃣ 团队成员活跃度 -->
        <a-divider />
        <div class="chart-container">
          <canvas ref="activityChart"></canvas>
        </div>

        <!-- 3️⃣ Issue 详细信息 -->
        <a-divider />
        <a-typography-title level="4" class="text-center mt-4">
          Issue Details
        </a-typography-title>
        <a-table
          :columns="columns"
          :data-source="issues"
          row-key="issue_id"
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

// 表格列
const columns = [
  { title: "Issue ID", dataIndex: "issue_id", key: "issue_id" },
  { title: "create time", dataIndex: "created_at", key: "created_at" },
  { title: "first team reply time", dataIndex: "first_team_reply_at", key: "first_team_reply_at" },
  { title: "response time (h)", dataIndex: "response_time_hours", key: "response_time_hours" },
  { title: "responded by team", dataIndex: "responded_by_team", key: "responded_by_team" },
];

const issues = ref([]);
const averageTime = ref(0);
const percent = computed(() => (averageTime.value > 0 ? Math.min((averageTime.value / 500) * 100, 100) : 0));
const activityChart = ref(null);

onMounted(async () => {
  const res = await fetch("/response_time.json");
  const data = await res.json();

  issues.value = data.issues_details || [];
  averageTime.value = data.average_response_time_hours || 0;

  const activity = {};
  data.issues_details.forEach((issue) => {
    if (issue.responded_by_team) {
      const responder = issue.first_team_reply_at ? data.team_members[0] : "Team";
      activity[responder] = (activity[responder] || 0) + 1;
    }
  });

  const ctx = activityChart.value.getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: Object.keys(activity),
      datasets: [
        {
          label: "Number of replies",
          data: Object.values(activity),
          backgroundColor: "#409EFF",
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
