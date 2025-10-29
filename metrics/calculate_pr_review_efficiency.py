import json
from datetime import datetime

def calculate_pr_review_efficiency(pr_data):
    """
    分析PR审查效率：只包含已关闭的PR
    efficiency_score：代码改动量与时间之比
    """
    results = []
    total_efficiency_score = 0
    total_merge_time = 0
    total_review_time = 0
    analyzed_pr_count = 0
    
    for pr in pr_data:
        # 只处理已关闭的PR
        if pr.get("merged_at") and pr["state"] == "closed":
            # 计算合并总时长（小时）
            created_time = datetime.fromisoformat(pr["created_at"].replace('Z', '+00:00'))
            merged_time = datetime.fromisoformat(pr["merged_at"].replace('Z', '+00:00'))
            merge_time_hours = (merged_time - created_time).total_seconds() / 3600
            
            # 计算审查次数（至少为1次）
            review_count = max(pr.get("review_comments", 0), 1)
            
            # 计算平均审查时间
            average_review_time_hours = merge_time_hours / review_count
            
            # 计算代码变更总量
            total_changes = pr.get("additions", 0) + pr.get("deletions", 0)
            
            # 计算效率评分：变更量/平均审查时间
            if average_review_time_hours > 0:
                efficiency_score = total_changes / average_review_time_hours
            else:
                efficiency_score = total_changes
            
            pr_info = {
                "pr_id": int(pr["id"]),
                "created_at": pr["created_at"],
                "merged_at": pr["merged_at"],
                "state": pr["state"],
                "merge_time_hours": round(merge_time_hours, 2),
                "average_review_time_hours": round(average_review_time_hours, 2),
                "total_changes": total_changes,
                "efficiency_score": round(efficiency_score, 2)
            }
            
            results.append(pr_info)
            
            total_efficiency_score += efficiency_score
            total_merge_time += merge_time_hours
            total_review_time += average_review_time_hours
            analyzed_pr_count += 1
    
    # 计算整体统计
    overall_stats = {}
    if analyzed_pr_count > 0:
        overall_stats = {
            "average_efficiency_score": round(total_efficiency_score / analyzed_pr_count, 2),
            "average_merge_time_hours": round(total_merge_time / analyzed_pr_count, 2),
            "average_review_time_hours": round(total_review_time / analyzed_pr_count, 2)
        }
    
    return {
        "overall_statistics": overall_stats,
        "pr_details": results
    }

# 示例使用
if __name__ == "__main__":
    # 示例输入数据
    input_data = [
        {
            "id": "123",
            "created_at": "2023-01-01T10:00:00Z",
            "merged_at": "2023-01-01T12:00:00Z",
            "state": "closed",
            "additions": 150,
            "deletions": 50,
            "review_comments": 2
        },
        {
            "id": "124", 
            "created_at": "2023-01-02T09:00:00Z",
            "merged_at": "2023-01-03T10:00:00Z",
            "state": "closed",
            "additions": 80,
            "deletions": 20,
            "review_comments": 4
        },
        {
            "id": "125",
            "created_at": "2023-01-03T14:00:00Z",
            "merged_at": None,
            "state": "open",
            "additions": 100,
            "deletions": 30,
            "review_comments": 1
        }
    ]
    
    # 计算PR审查效率
    result = calculate_pr_review_efficiency(input_data)
    
    # 输出结果
    print(json.dumps(result, indent=2))