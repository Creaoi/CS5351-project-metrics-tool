<template>
  <div class="dashboard-container">

    <!-- Issue Metrics 表 -->
    <div class="table-container">
      <a-card class="dashboard-card shadow-md rounded-2xl">
        <a-typography>
          <a-typography-title level="2" class="text-center">
            Issue Metrics Report
          </a-typography-title>
          <a-divider />
          <a-typography-title level="3" class="text-center">
            Monthly issue metrics report
          </a-typography-title>

          <!-- Metrics 表 -->
          <div class="table-wrapper">
            <a-table
              :columns="metricsColumns"
              :data-source="metricsData"
              :pagination="false"
              bordered
              row-key="Metric"
              size="middle"
              class="feishu-table"
            />
          </div>

          <!-- Summary 表 -->
          <div class="table-wrapper mt-6">
            <a-table
              :columns="summaryColumns"
              :data-source="summaryData"
              :pagination="false"
              bordered
              row-key="Metric"
              size="middle"
              class="feishu-table"
            />
          </div>
        </a-typography>
      </a-card>
    </div>

    <!-- Issue Comments 表 -->
    <div class="table-container mt-8">
      <a-card class="dashboard-card shadow-md rounded-2xl">
        <a-typography>
          <a-typography-title level="3">Issue Comments from Users</a-typography-title>
          <a-divider />

          <!-- ✅ 搜索栏区域 -->
          <div class="search-bar">
            <a-input-search
              v-model:value="searchQuery"
              placeholder="Search by title, author, or assignee"
              allow-clear
              enter-button="Search"
              @search="handleSearch"
            />
          </div>

          <a-collapse>
            <a-collapse-panel key="1" header="📋 Click to expand issue details">
              <div class="table-wrapper">
                <a-table
                  :columns="commentsColumns"
                  :data-source="filteredIssues"
                  :pagination="{ pageSize: 10 }"
                  row-key="html_url"
                  size="middle"
                  bordered
                  class="feishu-table"
                />
              </div>
            </a-collapse-panel>
          </a-collapse>
        </a-typography>
      </a-card>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from "vue";

const metricsData = ref([]);
const summaryData = ref([]);
const issuesData = ref([]);
const searchQuery = ref(""); // ✅ 搜索关键字

// Metrics 表列
const metricsColumns = [
  { title: "Metric", dataIndex: "Metric", key: "Metric" },
  { title: "Average", dataIndex: "Average", key: "Average" },
  { title: "Median", dataIndex: "Median", key: "Median" },
  { title: "90th percentile", dataIndex: "90th percentile", key: "90th percentile" },
];

// Summary 表列
const summaryColumns = [
  { title: "Metric", dataIndex: "Metric", key: "Metric" },
  { title: "Count", dataIndex: "Count", key: "Count" },
];

// Issue Comments 表列
const commentsColumns = [
  { title: "Title", dataIndex: "title", key: "Title" },
  {
    title: "URL",
    dataIndex: "html_url",
    key: "URL",
    customRender: (record) => {
      const text = record.html_url;
      return text ? h("a", { href: text, target: "_blank" }, text) : "";
    },
  },
  { title: "Assignee", dataIndex: "assignee", key: "Assignee" },
  { title: "Author", dataIndex: "author", key: "Author" },
  { title: "Time to first response", dataIndex: "time_to_first_response", key: "Response" },
  { title: "Time to close", dataIndex: "time_to_close", key: "Close" },
  { title: "Time to answer", dataIndex: "time_to_answer", key: "Answer" },
];

// ✅ 计算属性：根据搜索关键字过滤结果
const filteredIssues = computed(() => {
  if (!searchQuery.value.trim()) return issuesData.value;
  const q = searchQuery.value.toLowerCase();
  return issuesData.value.filter(
    (item) =>
      (item.title && item.title.toLowerCase().includes(q)) ||
      (item.author && item.author.toLowerCase().includes(q)) ||
      (item.assignee && item.assignee.toLowerCase().includes(q))
  );
});

// ✅ 点击搜索按钮时触发（可选优化）
const handleSearch = () => {
  // 实时计算属性已自动生效，这里可以留空或打印日志
  console.log("Searching:", searchQuery.value);
};

onMounted(async () => {
  try {
    const res = await fetch("/issue_metrics.json");
    const data = await res.json();

    metricsData.value = [
      {
        Metric: "Time to first response",
        Average: data.average_time_to_first_response,
        Median: data.median_time_to_first_response,
        "90th percentile": data["90_percentile_time_to_first_response"],
      },
      {
        Metric: "Time to close",
        Average: data.average_time_to_close,
        Median: data.median_time_to_close,
        "90th percentile": data["90_percentile_time_to_close"],
      },
      {
        Metric: "Time to answer",
        Average: data.average_time_to_answer,
        Median: data.median_time_to_answer,
        "90th percentile": data["90_percentile_time_to_answer"],
      },
    ];

    summaryData.value = [
      { Metric: "Number of items that remain open", Count: data.num_items_opened },
      { Metric: "Number of items closed", Count: data.num_items_closed },
      { Metric: "Total number of items created", Count: data.total_item_count },
    ];

    issuesData.value = data.issues || [];
  } catch (err) {
    console.error("读取 JSON 失败:", err);
  }
});
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

/* 卡片统一风格 */
.dashboard-card {
  padding: 20px;
  background: linear-gradient(180deg, #f8faff 0%, #ffffff 100%);
  border-radius: 16px;
}

/* 表格容器 */
.table-container {
  max-width: 900px;
  margin: 0 auto;
}

/* 搜索栏样式 */
.search-bar {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}

/* 飞书风格表格 */
.feishu-table {
  border: none;
}
.feishu-table th {
  background: transparent;
  color: #333;
  font-weight: 600;
  border-bottom: 1px solid rgba(0,0,0,0.1);
}
.feishu-table td {
  border-bottom: 1px solid rgba(0,0,0,0.05);
  color: #444;
}

/* 折叠卡片自适应宽度 */
.a-collapse {
  width: 100%;
}
.a-collapse-panel {
  padding: 0 !important;
}
.table-wrapper {
  overflow-x: auto;
}
</style>
