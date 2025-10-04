export function parseMarkdownTable(md) {
  const lines = md
    .split("\n")
    .map(l => l.trim())
    .filter(l => l.startsWith("|")); // 保留 | 开头的表格行

  if (lines.length < 2) return [];

  // 解析表头
  const headers = lines[0]
    .split("|")
    .map(h => h.trim())
    .filter(h => h && h !== "---"); // 去掉空和 --- 

  // 解析数据行
  return lines.slice(2).map(line => {
    const cells = line
      .split("|")
      .map(c => c.trim())
      .filter(c => c); // 保留非空格单元格

    let obj = {};
    headers.forEach((h, i) => {
      obj[h] = cells[i] || "";
    });
    return obj;
  }).filter(row => Object.values(row).some(v => v));
}
