from datetime import datetime

def prepare_burnout_input(issues):
    """
    Convert a list of GitHub Issue objects to input_json for generate_burnout.
    Automatically computes sprint_start and sprint_end from the issues.
    
    Args:
        issues (list): List of GitHub Issue objects or dicts.
        
    Returns:
        dict: input_json with keys 'sprint_start', 'sprint_end', 'issues'.
    """
    issues_list = []

    for issue in issues:
        if isinstance(issue, dict):
            created_at = issue.get("created_at")[:10]
            closed_at = issue.get("closed_at")[:10]
            number = issue.get("number")
            title = issue.get("title")
        else:
            created_at = issue.created_at.strftime("%Y-%m-%d") if hasattr(issue.created_at, "strftime") else issue.created_at
            closed_at = issue.closed_at.strftime("%Y-%m-%d") if hasattr(issue.closed_at, "strftime") else issue.closed_at
            number = issue.number
            title = issue.title

        if created_at:
            created_at = created_at[:10] if isinstance(created_at, str) else created_at.strftime("%Y-%m-%d")
        if closed_at:
            closed_at = closed_at[:10] if isinstance(closed_at, str) else closed_at.strftime("%Y-%m-%d")    

        issues_list.append({
            "number": number,
            "title": title,
            "created_at": created_at,
            "closed_at": closed_at,
        })

    all_dates = [datetime.strptime(issue["created_at"][:10], "%Y-%m-%d") for issue in issues_list if issue["created_at"]]
    if not all_dates:
        raise ValueError("No valid created_at dates found in issues.")
    
    sprint_start = min(all_dates).strftime("%Y-%m-%d")
    sprint_end = max(all_dates).strftime("%Y-%m-%d")

    input_json = {
        "sprint_start": sprint_start,
        "sprint_end": sprint_end,
        "issues": issues_list
    }

    return input_json