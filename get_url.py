from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import subprocess
import run
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
ENV_PATH = ".env"

@app.route("/update_env", methods=["POST"])
def update_env():
    data = request.get_json()
    gh_token = data.get("gh_token")
    repo_name = data.get("repo_name")  # 只传仓库名

    if not gh_token or not repo_name:
        return jsonify({"message": "缺少必要参数"}), 400

    # 读取现有 .env 文件
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []

    new_lines = []
    found_token = False
    found_query = False

    # 正则匹配 SEARCH_QUERY 行
    search_env_re = re.compile(r'^\s*SEARCH_QUERY\s*=\s*(?P<quote>["\']?)(?P<content>.*?)(?P=quote)?\s*$')
    repo_re = re.compile(r'(repo:github/)[^\s"]+')  # 匹配 repo:github/<xxx>

    for line in lines:
        # 替换 GH_TOKEN
        if line.startswith("GH_TOKEN = "):
            line = f'GH_TOKEN = "{gh_token}"\n'
            found_token = True
        # 替换 repo:github/<xxx> 部分
        m = search_env_re.match(line)
        if m:
            orig_content = m.group("content")
            if repo_re.search(orig_content):
                new_content = repo_re.sub(rf"\1{repo_name}", orig_content, count=1)
            else:
                # 如果原来没有 repo:github/...，就在开头加上
                new_content = f"repo:github/{repo_name} {orig_content}".strip()
            line = f'SEARCH_QUERY = "{new_content}"\n'
            found_query = True
        new_lines.append(line)

    # 文件中没有对应行，补上
    if not found_token:
        new_lines.append(f'GH_TOKEN = "{gh_token}"\n')
    if not found_query:
        # 如果 SEARCH_QUERY 不存在，写入默认后缀
        new_lines.append(f'SEARCH_QUERY = "repo:github/{repo_name} is:pr"\n')

    # 写回 .env
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
        f.flush()
        os.fsync(f.fileno())

    # 调用 run.py
    try:
        load_dotenv(".env")
        run.main()
        return jsonify({"message": "已更新 .env 并运行 run.py"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"message": f"运行 run.py 出错: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
