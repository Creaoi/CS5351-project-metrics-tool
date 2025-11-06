<template>
      <!-- ✅ 放在所有 layout 外部，成为独立悬浮按钮 -->
  <a-button
    type="primary"
    class="floating-export-btn"
    @click="exportToPDF"
  >
    Export PDF
  </a-button>
  <a-layout class="dashboard-layout">
    
    <!-- Header -->
    <a-layout-header class="header fancy-header">
      <div class="header-content">
        <div class="header-text">
          <h1>📊 GitHub Dashboard</h1>
          <p>Display project analysis indicators</p>
        </div>
        <!-- 图片 -->
        <div>
          <img src="/header_illustration.svg" alt="dashboard" class="header-img" />
        </div>
      </div>
    </a-layout-header>


    <a-layout>
      <!-- 可折叠侧边栏 -->
      <a-layout-sider
        width="180"
        collapsible
        v-model:collapsed="collapsed"
        class="sider"
      >
        <div class="sider-buttons">
          <a-button
            v-for="btn in sidebarButtons"
            :key="btn.key"
            type="default"
            block
            @click="activeCard = btn.key"
            class="sider-btn"
          >
            <component :is="btn.icon" class="sider-icon" />
            <span v-if="!collapsed" class="sider-label">{{ btn.label }}</span>
          </a-button>
        </div>
      </a-layout-sider>


      
      <!-- 主内容 -->
      <a-layout-content class="content">
        <div class="cards-grid">
          <a-card
            v-for="card in cards"
            :key="card.key"
            class="dashboard-card"
            hoverable
            @click="activeCard = card.key"
          >
            <img :src="card.image" class="card-image" alt="illustration" />
            <h3 class="card-title">{{ card.label }}</h3>
          </a-card>
        </div>
      </a-layout-content>


      <!-- 放大展示模态 -->
      <a-modal
        :visible="!!activeCard"
        width="80%"
        :footer="null"
        @cancel="activeCard = null"
      >
        <component
          :is="getActiveComponent(activeCard)"
          :collapsed="false"
        />
      </a-modal>
    </a-layout>
  </a-layout>
  <!-- ✅ 隐藏的完整分析区域 -->
  <div id="export-container" style="display: none;">
    <IssueMetrics />
    <BurnoutChart />
    <ActivityRate />
    <ResponseTime />
    <Efficiency />
  </div>
</template>

<script setup>
import { ref } from "vue";
import IssueMetrics from "@/components/IssueMetrics.vue";
import BurnoutChart from "@/components/BurnoutChart.vue";
import ActivityRate from "@/components/ActivityRate.vue";
import ResponseTime from "@/components/ResponseTime.vue";
import Efficiency from "@/components/Efficiency.vue";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";



import {
  BarChartOutlined,
  FireOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons-vue";

const collapsed = ref(false);
const activeCard = ref(null);

const sidebarButtons = [
  { key: "issues", label: "issue analysis", icon: BarChartOutlined },
  { key: "burnout", label: "burnout chart", icon: FireOutlined },
  { key: "contribution", label: "contribution", icon: TeamOutlined },
  { key: "response", label: "response time", icon: ClockCircleOutlined },
  { key: "efficiency", label: "efficiency", icon: ThunderboltOutlined },
];

// 卡片配置
const cards = [
  { key: "issues", label: "issue analysis", image: "../illustrations/issues.svg" },
  { key: "burnout", label: "burnout chart", image: "../illustrations/burnout.svg" },
  { key: "response", label: "response time", image: "../illustrations/response.svg" },
  { key: "contribution", label: "contribution", image: "../illustrations/contribution.svg" },
  { key: "efficiency", label: "efficiency", image: "../illustrations/efficiency.svg" },
];

// 根据 activeCard 获取对应组件
const getActiveComponent = (key) => {
  switch (key) {
    case "issues":
      return IssueMetrics;
    case "burnout":
      return BurnoutChart;
    case "contribution":
      return ActivityRate;
    case "response":
      return ResponseTime;
    case "efficiency":
      return Efficiency;
    default:
      return null;
  }
};


// 导出多页 PDF 功能
const exportToPDF = async () => {
  const exportContainer = document.getElementById("export-container");
  if (!exportContainer) return;

  // 临时显示导出区
  exportContainer.style.display = "block";

  // 获取容器内所有一级子节点（每个分析组件）
  const components = Array.from(exportContainer.children);

  const pdf = new jsPDF("p", "mm", "a4");

  for (let i = 0; i < components.length; i++) {
    const comp = components[i];

    // 用 html2canvas 截取当前组件
    const canvas = await html2canvas(comp, {
      scale: 2,
      useCORS: true,
      logging: false,
    });

    const imgData = canvas.toDataURL("image/png");
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

    // 第一页直接加，之后添加新页再加
    if (i > 0) pdf.addPage();
    pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
  }

  // 重新隐藏导出区
  exportContainer.style.display = "none";

  pdf.save("GitHub_Analysis_Report.pdf");
};


</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  background: linear-gradient(160deg, #f0f5ff 0%, #e3ecfa 30%, #edf3ff 100%);
}

/* Header 样式 */
.fancy-header {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  padding: 60px 100px;
  position: relative; /* ⬅ 为绝对定位的图片提供定位上下文 */
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
  overflow: hidden; /* 防止图片超出范围 */
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* 文本靠左对齐 */
  max-width: 60%; /* ⬅ 防止文字太宽挡住右侧图 */
  z-index: 2;
  position: relative;
}

.header-text h1 {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(90deg, #ffffff, #d6e4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-img {
  position: absolute; /* ⬅ 让图片固定在右上角 */
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  width: 220px; /* 根据需要调整大小 */
  height: auto;
  opacity: 0.9;
  z-index: 1; /* 图片在背景层，文字在上层 */
  pointer-events: none; /* 避免挡住点击事件 */
}


/* 侧边栏 */
/* ✅ 修改 1：去掉 sider 的内边距，防止按钮整体右偏 */
.sider {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  padding: 0; /* ← 原来是16px，这里改为0 */
  border-right: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

/* ✅ 修改 2：统一按钮容器的内边距 */
.sider-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px; /* ← 新增，用于留出统一内边距 */
  box-sizing: border-box; /* ← 防止溢出 */
}

/* ✅ 修改 3：让按钮占满整个侧边栏宽度并贴边 */
.sider-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  width: 100%; /* ← 占满父容器宽度 */
  box-sizing: border-box; /* ← 包含 padding，不挤出外边 */
  padding: 10px 12px; /* ← 内部左右留一点空隙 */
  border: none;
  background: transparent;
  text-align: left;
  transition: all 0.3s ease;
}

.sider-btn:hover {
  background: rgba(76, 139, 245, 0.1); /* ✅ 可选：悬停高亮 */
  border-radius: 8px;
}

.sider-icon {
  font-size: 18px;
}

.sider-label {
  white-space: nowrap;
}

/* 折叠状态样式 */
.ant-layout-sider-collapsed .sider-buttons {
  align-items: center;
  padding: 8px;
}

.ant-layout-sider-collapsed .sider-btn {
  justify-content: center;
  width: 48px;
  height: 48px;
  padding: 0;
}


.ant-layout-sider-collapsed .sider-label {
  display: none;
}

/* 主内容布局 */
.content {
  padding: 30px 40px;
}
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
  justify-items: center;
}

/* 方形卡片 */
.dashboard-card {
  width: 100%;
  aspect-ratio: 1 / 1; /* 保持正方形 */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 16px;
  transition: all 0.25s ease;
  background: linear-gradient(135deg, #ffffff, #f0f4ff);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}
.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 64, 255, 0.12);
}

/* 图表自适应 */
.dashboard-card canvas {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain;
  max-width: 95%;
  max-height: 95%;
}

/* 响应式 */
@media (max-width: 768px) {
  .fancy-header {
    flex-direction: column;
    text-align: center;
    padding: 40px 20px;
  }
  .header-img {
    margin-top: 20px;
    width: 180px;
  }
}
/* 缩略卡片图案样式 */
.card-image {
  width: 70%;
  height: auto;
  object-fit: contain;
  margin-bottom: 12px;
  transition: transform 0.3s ease;
}

.dashboard-card:hover .card-image {
  transform: scale(1.05);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #334;
  text-align: center;
  margin: 0;
}

/* 每行显示 4 个方形卡片 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
  justify-items: center;
}

.dashboard-card {
  background: white;
  aspect-ratio: 1 / 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
  transition: all 0.25s ease;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
}

.export-btn {
  background: #4c8bf5;
  border: none;
  color: white;
  font-weight: 600;
  border-radius: 8px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}

.export-btn:hover {
  background: #3a7be0;
}
.floating-export-btn {
  position: fixed;
  right: 40px;
  bottom: 40px;
  z-index: 1000;
  background: #4c8bf5;
  border: none;
  color: white;
  font-weight: 600;
  border-radius: 50px;
  padding: 16px 28px;

  display: flex;              /* ✅ 让内部内容成为flex容器 */
  align-items: center;        /* ✅ 垂直居中 */
  justify-content: center;    /* ✅ 水平居中 */

  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  transition: all 0.3s ease;
}


.floating-export-btn:hover {
  background: #3a7be0;
  transform: translateY(-2px);
}

</style>
