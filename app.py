# -*- coding: utf-8 -*-
"""
后端 Flask 应用
功能：
1. 接收前端传入的 GitHub Token 与仓库名；
2. 更新 .env 文件中的 GH_TOKEN 与 SEARCH_QUERY；
3. 调用 run.main() 执行分析；（请把新代码直接放到这里调用并生成文件，还是在data文件夹下就好，不用修改路径）
4. 调用 copy_files.copy_files_to_frontend() 将结果复制到前端；（这一步不用管，也不要修改.env文件里的环境变量,不然会报错！）
5. 返回执行状态给前端。

前端通过 /update_env 接口 POST 数据：
{
    "gh_token": "ghp_xxx...",
    "repo_name": "owner/repo"
}
"""

import os
import re
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# === 导入核心功能模块 ===
# run.py 与 copy_files.py 必须与本文件在同一目录下
try:
    import run
    import copy_files
except ImportError as e:
    print(f"❌ 无法导入依赖模块: {e}")
    sys.exit(1)

# === Flask 基础配置 ===
app = Flask(__name__)
CORS(app)  # 允许前端跨域访问后端接口

# === 项目路径 ===
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

# ----------------------------------------------------
# 工具函数：更新 .env 文件内容
# ----------------------------------------------------
def update_env_file(gh_token, repo_name):
    """
    更新 .env 文件中的 GH_TOKEN 与 SEARCH_QUERY。
    保留其他变量（例如 OUTPUT_FILE）。
    """
    print("\n--- 📝 开始更新 .env 文件 ---")

    env_vars = {}

    # 1️⃣ 读取现有 .env 文件内容
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(r"^\s*([A-Z_]+)\s*=\s*['\"]?(.*?)['\"]?\s*$", line)
                if match:
                    key, value = match.groups()
                    env_vars[key] = value
    else:
        print("⚠️ 未找到 .env 文件，将创建新文件。")

    # 2️⃣ 更新 GH_TOKEN
    env_vars["GH_TOKEN"] = gh_token.strip()

    # 3️⃣ 构造新的 SEARCH_QUERY
    old_query = env_vars.get("SEARCH_QUERY", "")
    # 匹配 repo:xxxx/xxxx
    repo_pattern = re.compile(r"repo:[^\s\"]+")
    if repo_pattern.search(old_query):
        # 替换旧 repo
        new_query = repo_pattern.sub(f"repo:{repo_name}", old_query)
    else:
        # 如果原来没有 repo:，就在开头添加
        new_query = f"repo:{repo_name} {old_query}".strip()

    # 确保末尾有 "is:issue"
    if not new_query.endswith("is:issue"):
        new_query = f"{new_query} is:issue"

    env_vars["SEARCH_QUERY"] = new_query

    # 4️⃣ 写回 .env 文件（保持 OUTPUT_FILE 不变）
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for key, value in env_vars.items():
            f.write(f"{key} = \"{value}\"\n")

    print("✅ .env 文件更新完成！")
    print(f"→ GH_TOKEN: {env_vars['GH_TOKEN'][:10]}...（已隐藏）")
    print(f"→ SEARCH_QUERY: {env_vars['SEARCH_QUERY']}")
    print(f"→ OUTPUT_FILE: {env_vars.get('OUTPUT_FILE', '(未定义)')}")


# ----------------------------------------------------
# 主接口：更新环境变量并执行分析
# ----------------------------------------------------
@app.route("/update_env", methods=["POST"])
def update_env_and_run():
    """
    当前端点击“开始分析”按钮时触发。
    功能：
      1. 接收 gh_token 与 repo_name；
      2. 更新 .env；
      3. 调用 run.main()；
      4. 调用 copy_files_to_frontend()；
      5. 返回结果。
    """
    try:
        data = request.get_json(force=True)
        gh_token = data.get("gh_token")
        repo_name = data.get("repo_name")

        # 参数校验
        if not gh_token or not repo_name:
            return jsonify({"message": "缺少必要参数 gh_token 或 repo_name"}), 400

        # 1️⃣ 更新 .env 文件
        update_env_file(gh_token, repo_name)

        # 2️⃣ 重新加载环境变量
        load_dotenv(ENV_PATH, override=True)
        print("✅ 已重新加载环境变量。")

        # 3️⃣ 执行核心分析函数
        # 3️⃣ 执行核心分析函数
        print("\n--- 🚀 执行分析脚本 run.main() ---")

        # ✅ 新增：切换到 data 目录执行分析
        data_dir = os.path.join(PROJECT_ROOT, "data")
        os.makedirs(data_dir, exist_ok=True)

        # 临时切换当前工作目录
        old_cwd = os.getcwd()
        os.chdir(data_dir)

        try:
            run.main()
            print("✅ run.main() 执行完成。")
        finally:
            # 切回原工作目录
            os.chdir(old_cwd)


        # 4️⃣ 将结果文件复制到前端 public 目录
        print("\n--- 📁 执行文件同步 copy_files.copy_files_to_frontend() ---")
        copy_files.copy_files_to_frontend()
        print("✅ 文件复制完成。")

        # 5️⃣ 返回成功响应
        with open("data/issue_metrics.md", "r", encoding="utf-8") as f:
            md_content = f.read()
        return md_content, 200, {"Content-Type": "text/markdown; charset=utf-8"}


    except Exception as e:
        # 捕获所有异常并返回错误信息
        print(f"❌ 后端执行出错: {e}")
        return jsonify({
            "message": f"执行失败: {type(e).__name__}: {str(e)}",
            "status": "error"
        }), 500


# ----------------------------------------------------
# 启动 Flask 服务
# ----------------------------------------------------
if __name__ == "__main__":
    if PROJECT_ROOT not in sys.path:
        sys.path.append(PROJECT_ROOT)

    print(f"🌐 Flask 后端启动中 (http://127.0.0.1:5000)")
    app.run(host="0.0.0.0", port=5000, debug=True) 