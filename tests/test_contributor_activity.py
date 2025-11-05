import unittest
import pytest
from metrics.calculate_contributor_activity import calculate_contributor_activity
import json
from types import SimpleNamespace
import pytest
from unittest.mock import MagicMock
from core.run_calculate_contributor_activity import collect_issue_data

class TestContributorActivity(unittest.TestCase):
    def test_calculate_contributor_activity(self):
        # 测试数据
        issues = [
            # Issue1 closed by alice, with two comments (alice and bob)
            {"id": 1, "state": "closed", "closed_by": "alice", "comments": [
                {"user": "alice"}, {"user": "bob"}
            ]},
            # Issue2 open with one comment by charlie
            {"id": 2, "state": "open", "comments": [
                {"user": "charlie"}
            ]},
            # Issue3 closed by bob, no comments
            {"id": 3, "state": "closed", "closed_by": "bob", "comments": []},
            # Issue4 closed but closed_by is None (should be ignored)
            {"id": 4, "state": "closed", "closed_by": None, "comments": [
                {"user": "dave"}
            ]},
            # Issue5 has repeated commenters
            {"id": 5, "state": "open", "comments": [
                {"user": "alice"}, {"user": "alice"}
            ]},
        ]
        expected_leaderboard = [
            {"user": "alice", "closed_issues": 1, "comments": 3, "total_contributions": 8},
            {"user": "bob", "closed_issues": 1, "comments": 1, "total_contributions": 6},
            {"user": "charlie", "closed_issues": 0, "comments": 1, "total_contributions": 1},
            {"user": "dave", "closed_issues": 0, "comments": 1, "total_contributions": 1},
        ]
        result = calculate_contributor_activity(issues)
        self.assertEqual(result, expected_leaderboard)

    def test_no_issues(self):
        assert calculate_contributor_activity([]) == []

    def test_missing_fields(self):
        issues = [
            {"id": 1, "state": "closed"},  # missing closed_by
            {"id": 2, "state": "open"},    # no comments
        ]
        expected_leaderboard = []
        result = calculate_contributor_activity(issues)
        self.assertEqual(result, expected_leaderboard)


def make_comment(login):  
    return SimpleNamespace(user=SimpleNamespace(login=login))  

def make_issue_obj(comments=None, closed_by_login=None, comments_raise=None):  
    """  
    comments: list of comment objects or None  
    closed_by_login: str or None  
    comments_raise: if set to Exception instance or callable, will be used to raise when comments() called  
    """  
    if comments is None:  
        comments = []  
    obj = SimpleNamespace()  
    if comments_raise is not None:  
        def raise_fn():  
            if isinstance(comments_raise, Exception):  
                raise comments_raise  
            else:  
                # assume callable  
                return comments_raise()  
        obj.comments = raise_fn  
    else:  
        obj.comments = lambda: comments  
    obj.closed_by = SimpleNamespace(login=closed_by_login) if closed_by_login is not None else None  
    return obj  

def make_issue_wrapper(repo_full="https://api.github.com/repos/owner/repo", number=1, state="open"):  
    return SimpleNamespace(repository_url=repo_full, number=number, state=state)  

class TestCollectIssueData(unittest.TestCase):
    def test_collect_issue_data_basic(self):  
        # test normal case
        issue_wrapper = make_issue_wrapper(number=5, state="closed")  
        issue_obj = make_issue_obj(comments=[make_comment("alice"), make_comment(None)], closed_by_login="bob")  

        fake_conn = MagicMock()  
        fake_conn.issue.return_value = issue_obj  

        res = collect_issue_data([issue_wrapper], fake_conn)  
        assert isinstance(res, list) and len(res) == 1  

        item = res[0]  
        assert item["state"] == "closed"  
        assert item["closed_by"] == "bob"  
        assert item["comments"] == [{"user": "alice"}]  # None commenter filtered out  

    def test_collect_issue_data_handles_missing_login(self):  
        # test case where comment.user has no login attribute
        issue_wrapper = make_issue_wrapper(number=6, state="open")  
        # comment.user has no login attribute  
        comment_no_login = SimpleNamespace(user=SimpleNamespace())  
        issue_obj = make_issue_obj(comments=[comment_no_login], closed_by_login=None)  

        fake_conn = MagicMock()  
        fake_conn.issue.return_value = issue_obj  

        res = collect_issue_data([issue_wrapper], fake_conn)  
        assert res[0]["comments"] == []  # missing login filtered  

    def test_collect_issue_data_comments_raises_and_function_behaviour(self):  
        # test case where comments() raises an exception
        issue_wrapper = make_issue_wrapper(number=7, state="open")  
        issue_obj = make_issue_obj(comments=None, comments_raise=Exception("comments not found"), closed_by_login=None)  

        fake_conn = MagicMock()  
        fake_conn.issue.return_value = issue_obj  

        with pytest.raises(Exception, match="comments not found"):  
            collect_issue_data([issue_wrapper], fake_conn)  

    def test_collect_issue_data_multiple_issues(self):  
        # test multiple issues
        issue_wrapper1 = make_issue_wrapper(number=9, state="closed")  
        issue_obj1 = make_issue_obj(comments=[make_comment("alice")], closed_by_login="bob")  

        issue_wrapper2 = make_issue_wrapper(number=10, state="open")  
        issue_obj2 = make_issue_obj(comments=[make_comment("charlie"), make_comment("dave")], closed_by_login=None)  

        fake_conn = MagicMock()  
        fake_conn.issue.side_effect = [issue_obj1, issue_obj2]  

        res = collect_issue_data([issue_wrapper1, issue_wrapper2], fake_conn)  
        assert len(res) == 2  

        assert res[0]["state"] == "closed"  
        assert res[0]["closed_by"] == "bob"  
        assert res[0]["comments"] == [{"user": "alice"}]  

        assert res[1]["state"] == "open"  
        assert res[1]["closed_by"] is None  
        assert res[1]["comments"] == [{"user": "charlie"}, {"user": "dave"}]

    def test_collect_issue_data_no_issues(self):  
        # test empty issues list
        fake_conn = MagicMock()  
        res = collect_issue_data([], fake_conn)  
        assert res == []
    
    def test_collect_issue_data_none_in_comments(self):  
        # test case where comments list contains None
        issue_wrapper = make_issue_wrapper(number=11, state="open")  
        issue_obj = make_issue_obj(comments=[make_comment("eve"), None, make_comment("frank")], closed_by_login=None)  

        fake_conn = MagicMock()  
        fake_conn.issue.return_value = issue_obj  

        res = collect_issue_data([issue_wrapper], fake_conn)  
        assert res[0]["comments"] == [{"user": "eve"}, {"user": "frank"}]  # None comment filtered out

    def test_collect_issue_data_not_list_comments(self):  
        # test case where comments() does not return a list
        issue_wrapper = make_issue_wrapper(number=12, state="open")  

        def comments_not_list():  
            return "not a list"  

        issue_obj = make_issue_obj(comments=None, comments_raise=comments_not_list, closed_by_login=None)  

        fake_conn = MagicMock()  
        fake_conn.issue.return_value = issue_obj  

        with pytest.raises(TypeError):  
            collect_issue_data([issue_wrapper], fake_conn)

    def test_collect_issue_data_closed_by_none_and_no_comments(self):  
        # test case where closed_by is None and no comments
        issue_wrapper = make_issue_wrapper(number=8, state="closed")  
        issue_obj = make_issue_obj(comments=[], closed_by_login=None)  

        fake_conn = MagicMock()  
        fake_conn.issue.return_value = issue_obj  

        res = collect_issue_data([issue_wrapper], fake_conn)  
        assert res[0]["closed_by"] is None  
        assert res[0]["comments"] == []  

    def test_collect_issue_data_closed_by_no_login(self):  
        # test case where closed_by has no login attribute
        issue_wrapper = make_issue_wrapper(number=13, state="closed")  
        closed_by_no_login = SimpleNamespace()  # no login attribute  
        issue_obj = make_issue_obj(comments=[], closed_by_login=None)  
        issue_obj.closed_by = closed_by_no_login  

        fake_conn = MagicMock()  
        fake_conn.issue.return_value = issue_obj  

        res = collect_issue_data([issue_wrapper], fake_conn)  
        assert res[0]["closed_by"] is None