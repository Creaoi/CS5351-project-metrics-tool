<template>
  <div class="table-container">   <!-- ✅ 新增容器 -->
    <a-card class="w-4/5 shadow-md rounded-2xl">
      <a-typography>
        <!-- 标题 -->
        <a-typography-title level="2" class="text-center">
          Issue Metrics Report
        </a-typography-title>
        <a-divider />

        <a-typography-title level="3" class="text-center">
          Monthly issue metrics report
        </a-typography-title>

        <!-- 第一张表 -->
        <div class="flex justify-center mt-6">
          <a-table
            :columns="metricsColumns"
            :data-source="issuesData.metrics"
            bordered
            pagination="false"
            class="w-3/4"
          />
        </div>

        <!-- 第二张表 -->
        <div class="flex justify-center mt-10">
          <a-table
            :columns="summaryColumns"
            :data-source="issuesData.summary"
            bordered
            pagination="false"
            class="w-2/3"
          />
        </div>
      </a-typography>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const issuesData = ref({
  metrics: [],
  summary: [],
});

// 第一张表列配置
const metricsColumns = [
  { title: "Metric", dataIndex: "Metric", key: "Metric" },
  { title: "Average", dataIndex: "Average", key: "Average" },
  { title: "Median", dataIndex: "Median", key: "Median" },
  { title: "90th percentile", dataIndex: "90th percentile", key: "90th percentile" },
];

// 第二张表列配置
const summaryColumns = [
  { title: "Metric", dataIndex: "Metric", key: "Metric" },
  { title: "Count", dataIndex: "Count", key: "Count" },
];

// 解析 Markdown 中的所有表格
function parseMarkdownTables(md) {
  const tables = md.split(/\n\s*\n/).filter((block) => block.includes("|"));
  return tables.map((table) => {
    const lines = table.trim().split("\n");
    const headers = lines[0].split("|").map((h) => h.trim()).filter(Boolean);

    return lines.slice(2).map((line) => {
      const cells = line.split("|").map((c) => c.trim()).filter(Boolean);
      let obj = {};
      headers.forEach((h, i) => {
        obj[h] = cells[i] || "";
      });
      return obj;
    });
  });
}

onMounted(async () => {
  const res = await fetch("/issue-metrics.md"); // public 目录下的文件
  const mdText = await res.text();
  const parsed = parseMarkdownTables(mdText);

  issuesData.value.metrics = parsed[0] || [];
  issuesData.value.summary = parsed[1] || [];

  console.log("解析结果：", issuesData.value);
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
