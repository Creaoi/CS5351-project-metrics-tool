import json
import os
from os.path import join, dirname, abspath
from metrics.calculate_pr_review_efficiency import calculate_pr_review_efficiency

def _safe_int(v, default=0):
    try:
        if v is None:
            return default
        return int(v)
    except Exception:
        return default

def _sum_pr_file_stats(full_pr):
    total_add = 0
    total_del = 0
    try:
        for f in full_pr.files():  
            adds = getattr(f, "additions", 0) or 0
            dels = getattr(f, "deletions", 0) or 0
            total_add += _safe_int(adds, 0)
            total_del += _safe_int(dels, 0)
    except Exception as e:
        print(f"Failed to sum per-file stats for PR #{getattr(full_pr, 'number', 'unknown')}: {e}")
        return 0, 0
    return total_add, total_del

def collect_pr_data(github_connection, owners_and_repositories):
    results = []
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
                try:
                    full_pr = repo_obj.pull_request(pr.number)

                    additions = getattr(full_pr, "additions", None)
                    deletions = getattr(full_pr, "deletions", None)
                    changed_files = _safe_int(getattr(full_pr, "changed_files", None), 0)

                    if (not additions or int(additions) == 0) and changed_files > 0:
                        a_sum, d_sum = _sum_pr_file_stats(full_pr)
                        if a_sum or d_sum:
                            additions = a_sum
                            deletions = d_sum
                    additions = _safe_int(additions, 0)
                    deletions = _safe_int(deletions, 0)
                    review_comments = _safe_int(getattr(full_pr, "review_comments", 0), 0)

                    pr_record = {
                        "id": str(_safe_int(getattr(full_pr, "number", None), 0)),
                        "created_at": full_pr.created_at.isoformat() if full_pr.created_at else None,
                        "merged_at": full_pr.merged_at.isoformat() if full_pr.merged_at else None,
                        "state": getattr(full_pr, "state", None),
                        "additions": additions,
                        "deletions": deletions,
                        "review_comments": review_comments
                    }

                    results.append(pr_record)

                except Exception as e:
                    print(f"Failed to fetch details for PR #{getattr(pr, 'number', 'unknown')} in {owner}/{repo}: {e}")
                    continue

        except Exception as e:
            print(f"Error while fetching PRs from {owner}/{repo}: {e}")

    print(f"Collected {len(results)} PR records in total.")
    return results

def run_3(github_connection, owners_and_repositories):
    input = collect_pr_data(github_connection, owners_and_repositories)

    # 调用计算PR效率的函数
    result = calculate_pr_review_efficiency(input)

    current_dir = dirname(abspath(__file__))
    output_file_path = join(current_dir, '..', 'data', 'calculate_pr_review_efficiency.json')    
    with open(output_file_path, "w", encoding="utf-8") as f:
        #json.dump(input, f, ensure_ascii=False, indent=2)
        json.dump(result, f, ensure_ascii=False, indent=2)