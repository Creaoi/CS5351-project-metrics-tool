import json
import os
from os.path import join, dirname, abspath
from metrics.calculate_contributor_activity import calculate_contributor_activity


def safe_get_login(user_obj):
    if user_obj is None:
        return None
    return getattr(user_obj, "login", None)

def collect_issue_data(issues, github_connection):
    result = []

    for issue in issues:
        repo_fullname = issue.repository_url.split("repos/")[-1]
        owner, repo = repo_fullname.split("/")

        issue_obj = github_connection.issue(owner, repo, issue.number)

        comments = []
        for comment in issue_obj.comments():
            commenter = safe_get_login(comment.user)
            if commenter:
                comments.append({"user": commenter})

        closed_by = safe_get_login(getattr(issue_obj, "closed_by", None))

        result.append({
            "state": issue.state,
            "closed_by": closed_by,
            "comments": comments
        })

    return result    
 
def run_calculate_contributor_activity(issues, github_connection):
    # input
    input = collect_issue_data(issues, github_connection)
    # 调用计算活跃度的函数
    result = calculate_contributor_activity(input)
    #获取输出后保存
    
    current_dir = dirname(abspath(__file__))
    output_file_path = join(current_dir, '..', 'data', 'calculate_contributor_activity.json')    
    with open(output_file_path, "w", encoding="utf-8") as f:
        #json.dump(input, f, ensure_ascii=False, indent=2)
        json.dump(result, f, ensure_ascii=False, indent=2)
    
