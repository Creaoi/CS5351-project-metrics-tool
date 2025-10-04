<template> 
  <div style="padding: 20px">
    <div class="table-container">   <!-- ✅ 新增容器 -->
      <a-card bordered shadow style="border-radius: 12px">
        <a-typography>
          <a-typography-title level="3">Issue Comments from users</a-typography-title>
          <a-divider />
          <!-- 概览部分 -->
          <!-- <div class="markdown-body" v-html="summaryContent"></div> -->
          <!-- 折叠的 Issue 表格 -->
          <a-collapse style="margin-top: 20px">
            <a-collapse-panel key="1" header="📋 Issues 详情（点击展开）">
              <a-table
                :columns="columns"
                :data-source="issuesData"
                :pagination="{ pageSize: 10 }"
                bordered
                row-key="URL"
              />
            </a-collapse-panel>
          </a-collapse>
        </a-typography>
      </a-card>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted } from "vue";
import { marked } from "marked";

// 用于存储数据
const summaryContent = ref("");
const issuesData = ref([]);

// 表格列配置
import { h } from "vue";

const columns = [
  { title: "Title", dataIndex: "Title", key: "Title" },
  {
    title: "URL",
    dataIndex: "URL",
    key: "URL",
    customRender: ({ text }) => {
      return text
        ? h("a", { href: text, target: "_blank", rel: "noopener noreferrer" }, text)
        : "";
    },
  },
  { title: "Assignee", dataIndex: "Assignee", key: "Assignee" },
  {
    title: "Author",
    dataIndex: "Author",
    key: "Author",
    customRender: ({ text }) => {
      if (!text) return "";
      // Markdown 里是 [名字](链接)，可以正则拆分一下
      const match = /\[(.+?)\]\((.+?)\)/.exec(text);
      if (match) {
        return h("a", { href: match[2], target: "_blank" }, match[1]);
      }
      return text;
    },
  },
  { title: "Time to first response", dataIndex: "Time to first response", key: "Response" },
  { title: "Time to close", dataIndex: "Time to close", key: "Close" },
  { title: "Time to answer", dataIndex: "Time to answer", key: "Answer" },
];


onMounted(async () => {
  const response = await fetch("/issue-metrics.md");
  const text = await response.text();

  // 找到大表格位置
  const splitIndex = text.indexOf("| Title | URL");
  if (splitIndex !== -1) {
    const summaryPart = text.slice(0, splitIndex);
    const issuesPart = text.slice(splitIndex);

    summaryContent.value = marked(summaryPart);

    // 解析 markdown 表格
    issuesData.value = parseMarkdownTable(issuesPart);
  } else {
    summaryContent.value = marked(text);
  }
});

// 将 markdown 表格转成 JSON
function parseMarkdownTable(md) {
  const lines = md.trim().split("\n");
  const headers = lines[0]
    .split("|")
    .map((h) => h.trim())
    .filter((h) => h);

  return lines
    .slice(2) // 去掉表头和分隔行
    .map((line) => {
      const cells = line.split("|").map((c) => c.trim());
      let obj = {};
      headers.forEach((h, i) => {
        obj[h] = cells[i + 1] || ""; // i+1 是因为第一个可能是空
      });
      return obj;
    });
}
</script>

<style scoped>
.table-container {
  max-width: 900px;   /* 控制最大宽度，例如 900px */
  margin: 0 auto;     /* 居中 */
}

.markdown-body {
  font-size: 14px;
  line-height: 1.6;
}
</style>
