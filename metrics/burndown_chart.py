from datetime import datetime, timedelta
import re

def _parse_story_points(issue):
    # 先读取可能存在的 story_points 字段
    if 'story_points' in issue:
        story_points_value = issue['story_points']
        
        if story_points_value is not None:
            return float(story_points_value)
    
    # 再检查 labels 中是 SP，story_points 或其他类似的
    if 'labels' in issue:
        labels = issue['labels']
        for label in labels:
            match = re.search(
                r'(?:SP|story[\s\-_]?points?)[\s:\-]*(\d+(?:\.\d+)?)', 
                label, 
                re.IGNORECASE
            )
            if match:
                return float(match.group(1))
    
    # 没有找到，就默认一个issue是一个point
    return 1.0

def generate_burnout(input_json):
    # 处理传入的开始结束时间
    sprint_start = datetime.strptime(input_json["sprint_start"], "%Y-%m-%d")
    sprint_end = datetime.strptime(input_json["sprint_end"], "%Y-%m-%d")

    # 获取 issues 列表
    issues = input_json["issues"]
    
    # 处理 story_points 和时间
    for issue in issues:
        issue['story_points'] = _parse_story_points(issue)
        issue['created_at'] = datetime.strptime(issue['created_at'], "%Y-%m-%d")
        if issue['closed_at']:
            issue['closed_at'] = datetime.strptime(issue['closed_at'], "%Y-%m-%d")
        else:
            issue['closed_at'] = None
    
    # 生成日期列表
    num_days = (sprint_end - sprint_start).days + 1
    dates = []
    for i in range(num_days):
        current_date = sprint_start + timedelta(days=i)
        dates.append(current_date)
    
    # 计算实际燃尽线
    actual = []
    total_points = 0

    for issue in issues:
        total_points += issue['story_points']
    
    for current_date in dates:
        remaining = 0
        
        for issue in issues:
            if issue['closed_at'] is None:
                remaining += issue['story_points']
            elif issue['closed_at'] > current_date:
                remaining += issue['story_points']
        
        actual.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "remaining_points": remaining
        })
    
    # 计算理想燃尽线
    ideal = []
    total_days = len(dates)
    
    for i in range(total_days):
        current_date = dates[i]
        
        # 公式：总点数 * (1 - 已过天数比例)
        if total_days > 1:
            remaining = total_points * (1 - i / (total_days - 1))
        else:
            remaining = total_points
        
        remaining = round(remaining, 2)
        
        ideal.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "remaining_points": remaining
        })
    
    # 返回结果
    return {
        "actual": actual,
        "ideal": ideal
    }

