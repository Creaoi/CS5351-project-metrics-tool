import requests
import json
import os
from os.path import join, dirname, abspath
from metrics.calculate_response_time import calculate_team_response_time

# get_team_members
def fetch_all_contributors(owners_and_repositories, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_contributors = set()

    for repo_info in owners_and_repositories:
        owner = repo_info["owner"]
        repo = repo_info["repository"]
        page = 1

        while True:
            url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=100&page={page}"
            resp = requests.get(url, headers=headers)
            data = resp.json()
            if isinstance(data, dict) and data.get("message"):
                print(f"Failed to fetch contributors for {owner}/{repo}: {data['message']}")
                break

            if not data:
                break

            all_contributors.update([c["login"] for c in data])

            if len(data) < 100:
                break
            page += 1

    team_members = list(all_contributors)
    return team_members

def build_issues_with_comments(issues, github_connection, owners_and_repositories):
    all_issues_data = []
    repo_info = owners_and_repositories[0]  
    owner = repo_info["owner"]
    repo = repo_info["repository"] 
    for issue in issues:
        issue_number = issue.number
        created_at = issue.created_at.isoformat() if hasattr(issue.created_at, "isoformat") else issue.created_at

        issue_info = {
            "id": issue_number,
            "created_at": created_at,
            "comments": []
        }

        try:
            issue_obj = github_connection.issue(owner, repo, issue_number)
        except Exception as e:
            print(f"Failed to fetch issue {owner}/{repo}#{issue_number}: {e}")
            continue

        try:
            for comment in issue_obj.comments():  
                comment_created_at = comment.created_at.isoformat() if hasattr(comment.created_at, "isoformat") else comment.created_at
                issue_info["comments"].append({
                    "created_at": comment_created_at,
                    "user": comment.user.login
                })
        except Exception as e:
            print(f"Failed to fetch comments for {owner}/{repo}#{issue_number}: {e}")

        all_issues_data.append(issue_info)

    return all_issues_data

def run_calculate_team_response_time(issues, github_connection, owners_and_repositories, token):
    team_members = fetch_all_contributors(owners_and_repositories, token)
    issues_data = build_issues_with_comments(issues, github_connection, owners_and_repositories)

    # 调用计算响应时间的函数
    result = calculate_team_response_time(issues_data, team_members)
    
    '''
    input = {
        "team_members": team_members,
        "issues": all_issues_data
    }'''

    current_dir = dirname(abspath(__file__))
    output_file_path = join(current_dir, '..', 'data', 'response_time.json')    
    with open(output_file_path, "w", encoding="utf-8") as f:
        #json.dump(input, f, ensure_ascii=False, indent=2)
        json.dump(result, f, ensure_ascii=False, indent=2)