<template>
  <div class="chart-container">
    <h2>Issue Daily Stats Line Chart</h2>
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import * as echarts from "echarts";

const chartRef = ref(null);

onMounted(async () => {
  // 加载 JSON 数据
  const res = await fetch("/daily_stats.json");
  const data = await res.json();

  // 准备 x 轴（日期）和 y 轴数据
  const dates = data.map(d => d.date);
  const itemsCreated = data.map(d => d.items_created);
  const itemsClosed = data.map(d => d.items_closed);
  const itemsOpen = data.map(d => d.items_open);

  // 初始化 ECharts
  const chart = echarts.init(chartRef.value);

  chart.setOption({
    tooltip: { trigger: "axis" },
    legend: { data: ["Created", "Closed", "Open"] },
    xAxis: { type: "category", data: dates },
    yAxis: { type: "value" },
    series: [
      { name: "Created", type: "line", data: itemsCreated },
      { name: "Closed", type: "line", data: itemsClosed },
      { name: "Open", type: "line", data: itemsOpen }
    ]
  });
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 900px;
  margin: auto;
}
.chart {
  width: 100%;
  height: 500px;
}
</style>
