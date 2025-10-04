<template>
  <div>
    <!-- 星空背景 -->
    <StarBackground />

    <!-- 内容 -->
    <div class="relative z-10">
      <OriginalTable01 />
      <IssueView />
      <BurnoutChart />
    </div>
  </div>
</template>

<script setup>
import IssueView from "./components/IssueView.vue";
import OriginalTable01 from "./components/OriginalTable01.vue";
import StarBackground from "./components/Background.vue"; // 引入刚才写的星空组件
import BurnoutChart from "./components/BurnoutChart.vue"; // 引入刚才写的燃尽图组件
</script>
