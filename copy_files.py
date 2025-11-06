# -*- coding: utf-8 -*-
import os
import shutil
import re
import json
import pandas as pd
# 这个代码主要是复制文件的，通过app.py生成的文件原本在data文件，
# 但是前端必须要在frontend/public文件夹下读取这些文件，
# 所以需要一个脚本把这些文件复制过去，如果只有md文件会顺便生成json文件

# ----------------------------------------------------
# Configuration Paths
# ----------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_SOURCE_DIR = os.path.join(PROJECT_ROOT, 'data')
FRONTEND_PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'frontend', 'public')
FILES_TO_COPY = [
    'burnout.json',
    'issue_metrics.json',
    'issue_metrics.md',
    'calculate_contributor_activity.json',
    'calculate_pr_review_efficiency.json',
    'response_time.json'
]


# ----------------------------------------------------
# 🧩 Step 1: Markdown → JSON
# ----------------------------------------------------
def convert_md_to_json(md_path, json_path):
    """将 issue_metrics.md 转换为 issue_metrics.json（稳定版）"""
    import io

    if not os.path.exists(md_path):
        print(f"⚠️ 未找到 Markdown 文件: {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取所有 Markdown 表格（每个表格至少两行）
    tables = re.findall(r"(\|.*?\|(?:\n\|.*?\|)+)", content, re.DOTALL)
    if len(tables) < 3:
        print(f"⚠️ 未检测到完整表格，请检查 {md_path}。检测到 {len(tables)} 张。")
        return

    # 辅助函数：清理 Markdown 表格并转为 DataFrame
    def parse_md_table(md_text):
        lines = [line.strip() for line in md_text.strip().split("\n") if line.strip()]
        # 去除分隔线行（例如 |---|---:|）
        lines = [line for line in lines if not re.match(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$", line)]
        if not lines:
            return pd.DataFrame()

        # 统一补齐每行分隔符数量
        max_pipes = max(line.count("|") for line in lines)
        fixed_lines = []
        for line in lines:
            parts = [p.strip() for p in line.split("|") if p.strip() != ""]
            while len(parts) < max_pipes - 1:
                parts.append("")
            fixed_lines.append("| " + " | ".join(parts) + " |")

        fixed_md = "\n".join(fixed_lines)
        df = pd.read_csv(io.StringIO(fixed_md), sep="|", engine="python")
        df = df.dropna(axis=1, how="all")
        df.columns = [c.strip() for c in df.columns]
        df = df.loc[:, df.columns.notna()]
        df = df[[c for c in df.columns if c and c != "---"]]
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df

    # --- 1️⃣ 概览表 ---
    df1 = parse_md_table(tables[0])
    print(f"🧾 第1张表列名: {list(df1.columns)}")

    overview = {}
    for _, row in df1.iterrows():
        metric = row.get("Metric") or row.iloc[0]
        overview[metric] = {
            "Average": row.get("Average"),
            "Median": row.get("Median"),
            "90th percentile": row.get("90th percentile")
        }

    # --- 2️⃣ 数量表 ---
    df2 = parse_md_table(tables[1])
    print(f"🧾 第2张表列名: {list(df2.columns)}")

    counts = {}
    for _, row in df2.iterrows():
        metric = row.get("Metric") or (row.iloc[0] if len(row) else None)
        count = row.get("Count") or (row.iloc[-1] if len(row) else None)
        if metric:
            try:
                counts[metric] = int(str(count).strip())
            except:
                counts[metric] = str(count).strip()

    # --- 3️⃣ Issues 表 ---
    df3 = parse_md_table(tables[2])
    print(f"🧾 第3张表列名: {list(df3.columns)}")

    issues = []
    for _, row in df3.iterrows():
        issues.append({
            "title": row.get("Title"),
            "url": row.get("URL"),
            "assignee": row.get("Assignee"),
            "author": row.get("Author"),
            "time_to_first_response": None if row.get("Time to first response") == "None" else row.get("Time to first response"),
            "time_to_close": None if row.get("Time to close") == "None" else row.get("Time to close"),
            "time_to_answer": None if row.get("Time to answer") == "None" else row.get("Time to answer"),
        })

    json_data = {
        "overview": overview,
        "counts": counts,
        "issues": issues
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功生成 JSON 文件: {json_path}")

# ----------------------------------------------------
# 🧩 Step 2: 复制文件到前端
# ----------------------------------------------------
def copy_files_to_frontend():
    print("--- 1. 复制文件到前端 Public 目录 ---")

    if not os.path.exists(FRONTEND_PUBLIC_DIR):
        print(f"⚠️ Public 目录不存在，创建中：{FRONTEND_PUBLIC_DIR}")
        os.makedirs(FRONTEND_PUBLIC_DIR, exist_ok=True)

    if not os.path.exists(DATA_SOURCE_DIR):
        print(f"❌ 错误：数据源目录不存在: {DATA_SOURCE_DIR}")
        return

    for filename in FILES_TO_COPY:
        source_path = os.path.join(DATA_SOURCE_DIR, filename)
        destination_path = os.path.join(FRONTEND_PUBLIC_DIR, filename)

        if os.path.exists(source_path):
            shutil.copy(source_path, destination_path)
            print(f"✅ 已复制 {filename} 到前端 public/")
        else:
            print(f"⚠️ 跳过 {filename}（未找到源文件）")


# ----------------------------------------------------
# 🏁 主执行逻辑
# ----------------------------------------------------
if __name__ == "__main__":
    md_path = os.path.join(DATA_SOURCE_DIR, "issue_metrics.md")
    json_path = os.path.join(DATA_SOURCE_DIR, "issue_metrics.json")

    print("=== 开始生成 issue_metrics.json ===")
    convert_md_to_json(md_path, json_path)

    print("\n=== 开始复制文件 ===")
    copy_files_to_frontend()

    print("\n✅ 全部流程完成！")
