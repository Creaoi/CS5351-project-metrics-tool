<template>
  <div class="markdown-container">
    <h2>📊 Issue Metrics Report</h2>
    <div v-html="htmlContent"></div>
  </div>
</template>

<script>
import { marked } from "marked"

export default {
  name: "MarkdownViewer",
  data() {
    return {
      htmlContent: ""
    }
  },
  mounted() {
    // 这里假设 issue_metrics.md 放在 public 目录下
    fetch("/issue_metrics.md")
      .then(res => res.text())
      .then(text => {
        this.htmlContent = marked(text) // 转换 Markdown → HTML
      })
  }
}
</script>

<style scoped>
.markdown-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  line-height: 1.6;
}

.markdown-container h1,
.markdown-container h2,
.markdown-container h3 {
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.markdown-container code {
  background: #f6f8fa;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>

