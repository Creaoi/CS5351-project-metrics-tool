from datetime import datetime, timedelta
import json
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock
from  metrics.calculate_response_time import calculate_team_response_time
from core.run_calculate_team_response_time import run_calculate_team_response_time,fetch_all_contributors,build_issues_with_comments
import pytest

TEAM = ["alice", "bob"]

class TestCalculateTeamResponseTime(unittest.TestCase):
    def test_no_comments():
        # Issue with no comments should yield zero response time
        issues = [{"id": 1, "created_at": "2025-11-01T08:00:00", "comments": []}]
        res = calculate_team_response_time(issues, TEAM)
        assert res["total_issues_count"] == 1
        assert res["responded_issues_count"] == 0
        assert res["average_response_time_hours"] == 0
        assert res["issues_details"][0]["responded_by_team"] is False

    def test_none_comments():
        # Issue with no comments should yield zero response time
        issues = [{"id": 1, "created_at": "2025-11-01T08:00:00", "comments": None}]
        res = calculate_team_response_time(issues, TEAM)
        assert res["total_issues_count"] == 1
        assert res["responded_issues_count"] == 0
        assert res["average_response_time_hours"] == 0
        assert res["issues_details"][0]["responded_by_team"] is False

    def test_team_reply_found():
        # Issue with a team member comment
        issues = [{"id": 2, "created_at": "2025-11-01T10:00:00", "comments": [
            {"user": "alice", "created_at": "2025-11-01T11:30:00"}
        ]}]
        res = calculate_team_response_time(issues, TEAM)
        assert res["responded_issues_count"] == 1
        assert res["average_response_time_hours"] == 1.5
        assert res["issues_details"][0]["response_time_hours"] == 1.5

    def test_multiple_comments_and_sorting():
        # Issue with multiple comments, ensuring sorting and correct response time calculation
        issues = [{"id": 3, "created_at": "2025-11-01T09:00:00", "comments": [
            {"user": "bob", "created_at": "2025-11-01T12:00:00"},
            {"user": "external", "created_at": "2025-11-01T09:10:00"}
        ]}]
        res = calculate_team_response_time(issues, TEAM)
        assert res["responded_issues_count"] == 1
        assert res["issues_details"][0]["response_time_hours"] == 3.0

    def test_no_team_replies():
        # Issue with comments but no team member replies
        issues = [{"id": 4, "created_at": "2025-11-01T09:00:00", "comments": [
            {"user": "external", "created_at": "2025-11-01T09:10:00"}
        ]}]
        res = calculate_team_response_time(issues, TEAM)
        assert res["responded_issues_count"] == 0
        assert res["average_response_time_hours"] == 0

    def test_mixed_issues():
        # Mixed issues with and without team replies
        issues = [
            {"id": 5, "created_at": "2025-11-01T08:00:00", "comments": []},
            {"id": 6, "created_at": "2025-11-01T10:00:00", "comments": [
                {"user": "alice", "created_at": "2025-11-01T11:00:00"}
            ]},
            {"id": 7, "created_at": "2025-11-01T09:00:00", "comments": [
                {"user": "external", "created_at": "2025-11-01T09:10:00"}
            ]}
        ]
        res = calculate_team_response_time(issues, TEAM)
        assert res["total_issues_count"] == 3
        assert res["responded_issues_count"] == 1
        assert res["average_response_time_hours"] == 1.0

    def test_empty_issues_list():
        # Empty issues list should yield zero response time
        issues = []
        res = calculate_team_response_time(issues, TEAM)
        assert res["total_issues_count"] == 0
        assert res["responded_issues_count"] == 0
        assert res["average_response_time_hours"] == 0

    def test_invalid_date_format(): 
        # Issue with invalid date format should be handled gracefully
        issues = [{"id": 8, "created_at": "invalid-date", "comments": [
            {"user": "alice", "created_at": "2025-11-01T11:00:00"}
        ]}]
        res = calculate_team_response_time(issues, TEAM)
        assert res["total_issues_count"] == 1
        assert res["responded_issues_count"] == 0
        assert res["average_response_time_hours"] == 0

    def test_reply_before_issue_creation():
        # Comment created before issue creation should be ignored
        issues = [{"id": 9, "created_at": "2025-11-01T10:00:00", "comments": [
            {"user": "bob", "created_at": "2025-11-01T09:00:00"}
        ]}]
        res = calculate_team_response_time(issues, TEAM)
        assert res["total_issues_count"] == 1
        assert res["responded_issues_count"] == 0
        assert res["average_response_time_hours"] == 0
    
    def test_no_team_members():
        # No team members should yield zero response time
        issues = [{"id": 10, "created_at": "2025-11-01T10:00:00", "comments": [
            {"user": "alice", "created_at": "2025-11-01T11:00:00"}
        ]}]
        res = calculate_team_response_time(issues, [])
        assert res["total_issues_count"] == 1
        assert res["responded_issues_count"] == 0
        assert res["average_response_time_hours"] == 0

class TestFetchAllContributors(unittest.TestCase):
    def test_fetch_all_contributors(monkeypatch):
        # normal case with two contributors 
        fake_resp = MagicMock()
        fake_resp.json.return_value = [
            {"login": "alice"},
            {"login": "bob"}
        ]
        monkeypatch.setattr("requests.get", lambda url, headers=None: fake_resp)

        repos = [{"owner": "o", "repository": "r"}]
        contributors = fetch_all_contributors(repos)
        assert set(contributors) == {"alice", "bob"}
    
    def test_fetch_all_contributors_api_failure(monkeypatch, capsys):
        # API returns an error message
        err = MagicMock()
        err.json.return_value = {"message": "Bad credentials"}
        monkeypatch.setattr("requests.get", lambda url, headers=None: err)
        repos = [{"owner": "o", "repository": "r"}]
        contributors = fetch_all_contributors(repos)
        captured = capsys.readouterr()
        assert "Failed to fetch contributors" in captured.out
        assert contributors == []

    def test_fetch_all_contributors_empty_repo(monkeypatch):
        # Repository with no contributors
        empty_resp = MagicMock()
        empty_resp.json.return_value = []
        monkeypatch.setattr("requests.get", lambda url, headers=None: empty_resp)
        repos = [{"owner": "o", "repository": "r"}]
        contributors = fetch_all_contributors(repos)
        assert contributors == []   
        

    def test_fetch_all_contributors_pagination(monkeypatch):
        # Simulate pagination with more than 100 contributors
        first = MagicMock()
        first.json.return_value = [{"login": f"user{i}"} for i in range(100)]
        second = MagicMock()
        second.json.return_value = [{"login": "last"}]
        calls = {"n": 0}

        def fake_get(url, headers=None):
            calls["n"] += 1
            return first if calls["n"] == 1 else second

        monkeypatch.setattr("requests.get", fake_get)
        repos = [{"owner": "o", "repository": "r"}]
        contributors = fetch_all_contributors(repos)
        assert "last" in contributors
        assert len(contributors) == 101
    
    def test_fetch_all_contributors_non_dict_response(monkeypatch):
        # API returns a non-dict, non-list response
        bad_resp = MagicMock()
        bad_resp.json.return_value = "unexpected string"
        monkeypatch.setattr("requests.get", lambda url, headers=None: bad_resp)
        repos = [{"owner": "o", "repository": "r"}]
        contributors = fetch_all_contributors(repos)
        assert contributors == []

class TestBuildIssuesWithComments(unittest.TestCase):
    def test_build_issues_with_comments(monkeypatch):
        # normal case

        # construct issue and comments, mock github_connection to return them
        comment1 = SimpleNamespace(created_at="2025-11-01T10:00:00", user=SimpleNamespace(login="alice"))
        comment2 = SimpleNamespace(created_at="2025-11-01T11:00:00", user=SimpleNamespace(login="external"))
        issue_obj = SimpleNamespace(comments=lambda: [comment1, comment2])

        fake_conn = MagicMock()
        fake_conn.issue.return_value = issue_obj

        fake_issue = SimpleNamespace(number=12, created_at="2025-11-01T09:00:00")
        owners_and_repositories = [{"owner": "o", "repository": "r"}]

        results = build_issues_with_comments([fake_issue], fake_conn, owners_and_repositories)
        assert len(results) == 1
        r = results[0]
        assert r["id"] == 12
        assert len(r["comments"]) == 2
        assert r["comments"][0]["user"] == "alice"

    def test_build_issues_with_comments_issue_error(monkeypatch, capsys):
        # Simulate error when fetching issue
        fake_conn = MagicMock()
        fake_conn.issue.side_effect = Exception("not found")

        fake_issue = SimpleNamespace(number=13, created_at="2025-11-01T09:00:00")
        owners_and_repositories = [{"owner": "o", "repository": "r"}]

        results = build_issues_with_comments([fake_issue], fake_conn, owners_and_repositories)
        
        assert results == []

    def test_build_issues_with_comments_comment_error(monkeypatch, capsys):
        # Simulate error when fetching comments
        def raise_exception():
            raise Exception("comments not found")

        issue_obj = SimpleNamespace(comments=raise_exception)

        fake_conn = MagicMock()
        fake_conn.issue.return_value = issue_obj

        fake_issue = SimpleNamespace(number=14, created_at="2025-11-01T09:00:00")
        owners_and_repositories = [{"owner": "o", "repository": "r"}]

        results = build_issues_with_comments([fake_issue], fake_conn, owners_and_repositories)
        assert len(results) == 1
        r = results[0]
        assert r["id"] == 14
        assert r["comments"] == []

    def test_build_issues_with_comments_missing_login(monkeypatch):
        # Comment with missing user login
        comment1 = SimpleNamespace(created_at="2025-11-01T10:00:00", user=SimpleNamespace(login=None))
        issue_obj = SimpleNamespace(comments=lambda: [comment1])

        fake_conn = MagicMock()
        fake_conn.issue.return_value = issue_obj

        fake_issue = SimpleNamespace(number=15, created_at="2025-11-01T09:00:00")
        owners_and_repositories = [{"owner": "o", "repository": "r"}]

        results = build_issues_with_comments([fake_issue], fake_conn, owners_and_repositories)
        assert len(results) == 1
        r = results[0]
        assert r["id"] == 15
        assert r["comments"][0]["user"] is None