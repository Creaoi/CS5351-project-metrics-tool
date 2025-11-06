import json

def calculate_contributor_activity(issues_data):
    # 初始化贡献者列表
    contributors = {}
    
    # 遍历所有issues
    for issue in issues_data:
        # 处理关闭issue的用户
        if issue.get("state") == "closed" and issue.get("closed_by"):
            closer = issue["closed_by"]
            if closer not in contributors:
                contributors[closer] = {"closed": 0, "commented": 0, "total": 0}
            contributors[closer]["closed"] += 1
            contributors[closer]["total"] += 5
        
        # 处理评论
        comments = issue.get("comments", [])
        for comment in comments:
            commenter = comment["user"]
            if commenter not in contributors:
                contributors[commenter] = {"closed": 0, "commented": 0, "total": 0}
            contributors[commenter]["commented"] += 1
            contributors[commenter]["total"] += 1
    
    # 转换为排行榜列表
    leaderboard = []
    for user, stats in contributors.items():
        leaderboard.append({
            "user": user,
            "closed_issues": stats["closed"],
            "comments": stats["commented"],
            "total_contributions": stats["total"]
        })
    
    # 按总贡献度排序
    leaderboard.sort(key=lambda x: x["total_contributions"], reverse=True)
    
    return leaderboard