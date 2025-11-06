<template>
  <a-layout class="analyze-layout">
    <!-- 页头 -->
    <a-layout-header class="header fancy-header">
      <div class="header-content">
        <div class="header-text">
          <h1>📊 GitHub Metrics Dashboard</h1>
          <p>Enter the repository and token information to begin analyzing project metrics.</p>
        </div>
        <img src="/header_illustration.svg" alt="analysis" class="header-img" />
      </div>
    </a-layout-header>
    <a-layout>
      <!-- 侧边栏 -->
      <a-layout-sider
        width="150"
        class="sider"
        collapsible
        v-model:collapsed="isCollapsed"
        breakpoint="lg"
      >
        <div class="sider-buttons" v-if="!isCollapsed">
          <a-button
            type="primary"
            ghost
            block
            @click="showTutorial = true"
          >
            Get Token Tutorial
          </a-button>
          <a-button
            type="default"
            block
            @click="openGithub"
          >
            Go To GitHub
          </a-button>
        </div>
      </a-layout-sider>


      <!-- 主内容 -->
      <a-layout-content class="content">
        <a-card
          class="main-card"
          bordered
          hoverable
        >
          <a-form layout="vertical">
            <!-- ✅ 仓库输入 -->
            <a-form-item label="Target repositories (Owner/RepoName)">
              <a-input
                v-model:value="repoName"
                placeholder="repo: vuejs/core"
                allow-clear
              />
            </a-form-item>

            <!-- ✅ Token 输入 -->
            <a-form-item label="GitHub Personal Access Token (PAT)">
              <a-input-password
                v-model:value="ghToken"
                placeholder="Please Enter GitHub Token"
                allow-clear
              />
            </a-form-item>

            <!-- 开始按钮 -->
            <a-button
              type="primary"
              block
              :loading="isAnalyzing"
              @click="handleClick"
            >
              {{ isAnalyzing ? statusMessage : "Start Analysis" }}
            </a-button>

            <!-- 状态提示 -->
            <a-alert
              v-if="statusMessage"
              :message="statusMessage"
              :type="statusType"
              show-icon
              class="mt-4"
            />
          </a-form>
        </a-card>
      </a-layout-content>
    </a-layout>

    <!-- Token 获取教程弹窗 -->
    <a-modal
      :visible="showTutorial"
      title="🔑 how to get your own GitHub Token"
      :footer="null"
      width="70%"
      centered
      @cancel="showTutorial = false"
    >
      <div style="padding: 20px">
        <a-steps :current="currentStep" size="small" style="margin-bottom: 30px">
          <a-step title="Open GitHub and go to settings" />
          <a-step title="Find Developer settings" />
          <a-step title="Create a new Token" />
          <a-step title="Copy Token" />
        </a-steps>

        <div style="text-align: center">
          <img
            :src="steps[currentStep].img"
            :alt="steps[currentStep].title"
            style="width: 80%; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1)"
          />
          <p style="margin-top: 20px; color: #333; font-weight: 500">
            {{ steps[currentStep].desc }}
          </p>
        </div>

        <div style="display: flex; justify-content: space-between; margin-top: 30px">
          <a-button @click="prevStep" :disabled="currentStep === 0">Previous Step</a-button>
          <a-button type="primary" @click="nextStep" :disabled="currentStep === steps.length - 1">
            Next Step
          </a-button>
        </div>
      </div>
    </a-modal>
  </a-layout>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { message } from "ant-design-vue";

const router = useRouter();
const ghToken = ref("");
const repoName = ref("");
const isAnalyzing = ref(false);
const statusMessage = ref("");
const statusType = ref("info");
const showTutorial = ref(false);
const currentStep = ref(0);
// 新增：
const isCollapsed = ref(false);

const steps = [
  {
    title: "Open GitHub and go to settings",
    desc: "Visit https://github.com and log in to your account. Click on your profile picture in the top right corner and select Settings.",
    img: "../tokentutorial/tutorial_step1.png",
  },
  {
    title: "Find Developer settings",
    desc: "Click on Developer settings.",
    img: "../tokentutorial/tutorial_step2.png",
  },
  {
    title: "Create a new Token",
    desc: "Go to Personal access tokens → Tokens (classic) → Generate new token (classic).",
    img: "../tokentutorial/tutorial_step3.png",
  },
  {
    title: "Copy Token",
    desc: "The generated token will only be displayed once. Please be sure to copy it and paste it into the input box above. Keep it safe!",
    img: "../tokentutorial/tutorial_step4.png",
  },
];

const API_URL = "/api/update_env";

// ✅ 修正版 handleClick
const handleClick = () => {
  console.log("handleClick:", {
    repoName: repoName.value,
    ghToken: ghToken.value,
  });

  const repoTrimmed = String(repoName.value ?? "").trim();
  const tokenTrimmed = String(ghToken.value ?? "").trim();

  if (!repoTrimmed || !tokenTrimmed) {
    message.warning("please fill in the complete repository name and GitHub Token!");
    return;
  }

  repoName.value = repoTrimmed;
  ghToken.value = tokenTrimmed;

  startAnalysis();
};

const startAnalysis = async () => {
  if (!ghToken.value || !repoName.value) return;

  isAnalyzing.value = true;
  statusMessage.value = "analysis has started, please wait...";
  statusType.value = "info";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        gh_token: ghToken.value,
        repo_name: repoName.value,
      }),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Unknown error");
    }

    statusMessage.value = "Analysis complete! Data has been updated.";
    statusType.value = "success";
    message.success("Analysis complete!");

    setTimeout(() => {
      router.push("/dashboard");
    }, 600);
  } catch (err) {
    console.error(err);
    statusMessage.value = "Network or server error: " + err.message;
    statusType.value = "error";
    message.error("Analysis failed: " + err.message);
  } finally {
    isAnalyzing.value = false;
  }
};

const nextStep = () => {
  if (currentStep.value < steps.length - 1) currentStep.value++;
};

const prevStep = () => {
  if (currentStep.value > 0) currentStep.value--;
};

const openGithub = () => {
  window.open("https://github.com", "_blank");
};
</script>

<style scoped>
.analyze-layout {
  min-height: 100vh;
  background: linear-gradient(180deg, #f4f8ff 0%, #e9f1fb 100%);
}

.header {
  background-color: #3a7afe;
  color: white;
  text-align: center;
  padding: 40px 0;         /* 上下内边距更大 */
  height: 120px;           /* 让 Header 更高 */
  display: flex;
  flex-direction: column;
  justify-content: center; /* 垂直居中 */
}


.title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 4px 0 0;
}

.sider {
  background: #f0f4ff;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sider-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 30px;
}

.content {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 20px 60px; /* ✅ 减小上边距 */
  margin-top: 0;
}



.main-card {
  width: 100%;
  max-width: 600px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 14px rgba(58, 122, 254, 0.15);
  transition: transform 0.3s ease;
}

.main-card:hover {
  transform: translateY(-3px);
}

.mt-4 {
  margin-top: 16px;
}

/* ====== 页面整体优化样式 ====== */

/* 让背景更柔和 */
.analyze-layout,
.analyze-layout .ant-layout {
  background: linear-gradient(160deg, #f0f5ff 0%, #e3ecfa 30%, #edf3ff 100%) !important;
}


/* Header 美化 */
.header {
  background: linear-gradient(90deg, #4a7dfc, #1d5fff);
  color: white;
  text-align: center;
  padding: 40px 0;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}
.title {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 15px;
  opacity: 0.95;
  color: #f0f6ff;
}

/* 主卡片提升层次 */
.main-card {
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 10px 30px rgba(0, 64, 255, 0.08);
  padding: 20px 30px;
  transition: all 0.3s ease;
}

.main-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 64, 255, 0.12);
}

/* 侧边栏微调 */
.sider {
  background: rgba(255, 255, 255, 0.6); /* ✅ 半透明白，不会破坏渐变层 */
  backdrop-filter: blur(8px);            /* ✅ 加微玻璃感 */
  padding: 16px;
  border-right: 1px solid rgba(255, 255, 255, 0.3);
}

.sider-buttons a-button {
  border-radius: 10px;
  font-weight: 500;
}

/* 输入框和按钮统一风格 */
.ant-input,
.ant-input-password {
  border-radius: 8px;
}

.ant-btn-primary {
  border-radius: 8px;
  background: linear-gradient(90deg, #3a7afe, #547eff);
  border: none;
}

.ant-btn-primary:hover {
  background: linear-gradient(90deg, #547eff, #3a7afe);
  transform: scale(1.02);
  transition: all 0.2s;
}


/* 教程弹窗样式 */
.ant-modal {
  border-radius: 16px !important;
}

.ant-steps-item-title {
  font-size: 14px;
  font-weight: 500;
}

.ant-modal-body {
  background: #f9fbff;
  border-radius: 0 0 16px 16px;
}

/* ===== 改造 Header 区域：企业感 + 插画风 ===== */
.fancy-header {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  padding: 60px 100px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
  position: relative;
  overflow: hidden;
}

/* ===== 改造 Header 区域：企业感 + 插画风 ===== */
.fancy-header {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  padding: 60px 100px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
  position: relative;
  overflow: hidden;
}

/* ===== 改造 Header 区域：企业感 + 插画风 ===== */
.fancy-header {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  padding: 60px 100px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
  position: relative;
  overflow: hidden;
}

/* 背景装饰图形，模拟飞书/钉钉那种渐变云雾感 */
.fancy-header::before {
  content: "";
  position: absolute;
  top: -50px;
  right: -80px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.25) 0%, transparent 70%);
  filter: blur(60px);
  z-index: 0;
}

/* 左侧文字块 */
.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  z-index: 2;
}

.header-text {
  text-align: left;
}

/* 渐变文字：避免 Vite 报错，使用 class + !important */
.header-text h1 {
  font-size: 30px;
  font-weight: 700;
  margin: 0 0 10px;
  letter-spacing: 0.6px;
  background: linear-gradient(90deg, #ffffff, #d6e4ff);
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  color: transparent; /* fallback */
}

.header-text p {
  font-size: 16px;
  color: #e9f1ff;
  opacity: 0.95;
  margin: 0;
}

/* 右侧插画 */
.header-img {
  width: 220px;
  max-height: 140px;
  object-fit: contain;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

/* ===== 响应式 ===== */
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

</style>

