import json
from datetime import datetime

def calculate_team_response_time(issues_data, team_members):
    total_response_time = 0
    responded_issues = 0
    results = []
    
    for issue in issues_data:
        # 获取issue创建时间
        created_at = datetime.fromisoformat(issue["created_at"])
        
        first_team_reply_time = None
        response_hours = None
        
        # 检查是否有评论
        if issue.get("comments") and len(issue["comments"]) > 0:
            # 按时间排序所有评论
            sorted_comments = sorted(
                issue["comments"], 
                key=lambda c: datetime.fromisoformat(c["created_at"])
            )
            
            # 找到最早的团队成员评论
            for comment in sorted_comments:
                if comment["user"] in team_members:
                    first_team_reply_time = datetime.fromisoformat(comment["created_at"])
                    break
            
            # 如果找到了团队回复
            if first_team_reply_time:
                # 计算响应时间（秒）
                response_seconds = (first_team_reply_time - created_at).total_seconds()
                
                # 转换为小时
                response_hours = response_seconds / 3600
                
                # 更新统计数据
                total_response_time += response_hours
                responded_issues += 1
        
        # 记录当前issue的分析结果
        results.append({
            "issue_id": issue.get("id", "N/A"),
            "created_at": issue["created_at"],
            "first_team_reply_at": first_team_reply_time.isoformat() if first_team_reply_time else None,
            "response_time_hours": round(response_hours, 2) if response_hours is not None else None,
            "responded_by_team": first_team_reply_time is not None
        })
    
    # 计算平均响应时间
    if responded_issues > 0:
        avg_response_time = total_response_time / responded_issues
    else:
        avg_response_time = 0
    
    # 返回结果
    return {
        "average_response_time_hours": round(avg_response_time, 2),
        "responded_issues_count": responded_issues,
        "total_issues_count": len(issues_data),
        "team_members": team_members,
        "issues_details": results
    }