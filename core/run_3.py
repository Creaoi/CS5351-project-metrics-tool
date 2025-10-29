import json
import os
from os.path import join, dirname, abspath

def collect_pr_data(github_connection, owners_and_repositories):
    all_pr_data = []

    for item in owners_and_repositories:
        owner = item.get("owner")
        repo = item.get("repository")

        if not owner or not repo:
            print("Invalid repository info:", item)
            continue

        print(f"Fetching PRs from {owner}/{repo} ...")

        try:
            repo_obj = github_connection.repository(owner, repo)
            pulls = repo_obj.pull_requests(state="all")

            for pr in pulls:
                pr_data = {
                    "id": pr.id,
                    "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                    "state": pr.state
                }
                all_pr_data.append(pr_data)

        except Exception as e:
            print(f"Error while fetching PRs from {owner}/{repo}: {e}")

    print(f"Collected {len(all_pr_data)} PR records in total.")
    return all_pr_data

def run_3(github_connection, owners_and_repositories):
    input = collect_pr_data(github_connection, owners_and_repositories)

    # 调用计算PR效率的函数
    # result = 

    current_dir = dirname(abspath(__file__))
    output_file_path = join(current_dir, '..', 'data', '333.json')    
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(input, f, ensure_ascii=False, indent=2)
        #json.dump(result, f, ensure_ascii=False, indent=2)