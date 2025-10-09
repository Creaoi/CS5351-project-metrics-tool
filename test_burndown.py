from types import SimpleNamespace
import unittest
import pytest
from datetime import datetime
from run_burndown import prepare_burnout_input
from burndown_chart import _parse_story_points,generate_burnout

class TestPrepareBurnoutInput(unittest.TestCase):
    """
    Test for prepare_burnout_input function
    """
    def test_prepare_with_dicts_and_iso_timestamps(self):
        """
        Test that function taking dicts with ISO timestamps or missing times as input returns correctly formatted dates and correct calculation result
        """
        issues = [
            {"created_at": "2025-10-01T09:00:00Z", "closed_at": "", "number": 1, "title": "one"},
            {"created_at": "2025-10-03T00:00:00Z", "closed_at": None, "number": 2, "title": "two"},
        ]
        res = prepare_burnout_input(issues)
        assert res["sprint_start"] == "2025-10-01"
        assert res["sprint_end"] == "2025-10-03"
        assert len(res["issues"]) == 2
        assert res["issues"][0]["created_at"] == "2025-10-01"
        assert res["issues"][0]["closed_at"] == "2025-10-02"
        assert res["issues"][1]["closed_at"] is None

    def test_prepare_with_datetime_objects(self):
        """
        Test that function taking object with datetime or missing times as input returns correctly formatted dates
        """
        issues = [
            SimpleNamespace(created_at=datetime(2025,10,2,12,0,0), closed_at="", number=10, title="dt"),
            SimpleNamespace(created_at=datetime(2025,9,30), closed_at=None, number=11, title="dt2"),
        ]
        res = prepare_burnout_input(issues)
        assert res["sprint_start"] == "2025-09-30"
        assert res["sprint_end"] == "2025-10-02"
        # make sure each field is of type string
        for it in res["issues"]:
            assert isinstance(it["created_at"], str)

    def test_prepare_mixed_input(self):
        """
        Test that function with mixed input and lacking of closed time field returns correct calculation result
        """
        issues = [
            {"created_at": "2025-05-05", "closed_at": None,  "number": 5, "title": "a"},
            SimpleNamespace(created_at="2025-05-07", closed_at="2025-05-08", number=6, title="b"),
        ]
        res = prepare_burnout_input(issues)
        assert res["sprint_start"] == "2025-05-05"
        assert res["sprint_end"] == "2025-05-07"

    def test_prepare_with_cross_month_dates(self):
        """
        Test that function with cross-month creating times returns correct calculation result
        """
        issues = [
            {"created_at": "2025-04-30", "closed_at": None, "number": 3, "title": "x"},
            {"created_at": "2025-05-02", "closed_at": None, "number": 4, "title": "y"},
        ]
        res = prepare_burnout_input(issues)
        assert res["sprint_start"] == "2025-04-30"
        assert res["sprint_end"] == "2025-05-02"
    
    def test_prepare_single_issue(self):
        """
        Test that function with single issue returns correct calculation result
        """
        issues = [
            {"created_at": "2025-05-07", "number": 7, "title": "c"},
        ]
        res = prepare_burnout_input(issues)
        assert res["sprint_start"] == "2025-05-07"
        assert res["sprint_end"] == "2025-05-07"
    
    def test_prepare_no_issues(self):
        """
        Test that function with empty issue list returns ValueError
        """
        issues = []
        with pytest.raises(ValueError):
            prepare_burnout_input(issues)

    def test_no_created_at_raises(self):
        """
        Test that function without create time input returns ValueError
        """
        issues = [
            {"created_at": None, "closed_at": None, "number": 1, "title": "no"},
            SimpleNamespace(created_at=None, closed_at=None, number=2, title="no2"),
        ]
        with pytest.raises(ValueError):
            prepare_burnout_input(issues)

    def test_invalid_date_format_raises(self):
        """
        Test that function with invalid date format input returns ValueError
        """
        issues = [
            {"created_at": "2025/06/01", "closed_at": None, "number": 8, "title": "bad"},
            {"created_at": "2025-06-02", "closed_at": None, "number": 9, "title": "good"},
        ]
        with pytest.raises(ValueError):
            prepare_burnout_input(issues)

    def test_single_issue_start_equals_end(self):
        """
        Test that function with the same creating and closing times input returns correct calculation result
        """
        issues = [
            {"created_at": "2024-12-12T00:00:00Z", "closed_at": None, "number": 99, "title": "single"}
        ]
        res = prepare_burnout_input(issues)
        assert res["sprint_start"] == res["sprint_end"] == "2024-12-12"


class TestGenerateBurnout(unittest.TestCase):
    """
    Test for _parse_story_points and generate_burnout function
    """
    def test_parse_story_points_field(self):
        """
        Test that issue with story_points field returns corect value
        """
        issue = {'story_points': 5}
        assert _parse_story_points(issue) == 5.0
    
    def test_parse_story_points_field_float(self):
        """
        Test that issue with story_points field as float returns corect value
        """
        issue = {'story_points': 2.5}
        assert _parse_story_points(issue) == 2.5
    
    def test_parse_story_points_field_str(self):
        """
        Test that issue with story_points field as string returns corect value
        """
        issue = {'story_points': '4'}
        assert _parse_story_points(issue) == 4.0
    
    def test_parse_story_points_label(self):
        """
        Test that issue with story_points in label returns corect value
        """
        issue = {'labels': ['SP:3']}
        assert _parse_story_points(issue) == 3.0

    def test_parse_story_points_label_multiple(self):
        """
        Test that issue with different story_points label formats returns corect value
        """
        issue = {'labels': ['story_points-2', 'other']}
        assert _parse_story_points(issue) == 2.0

    def test_parse_story_points_label_case_insensitive(self):
        """
        Test that issue with story_points label in different cases returns corect value
        """
        issue = {'labels': ['sp 1.5']}
        assert _parse_story_points(issue) == 1.5

    def test_parse_story_points_label_invalid(self):
        """
        Test that issue with invalid story_points label returns default value 1.0
        """
        issue = {'labels': ['no points here']}
        assert _parse_story_points(issue) == 1.0

    def test_parse_story_points_default(self):
        """
        Test that issue without story points info defaults to 1.0
        """
        issue = {}
        assert _parse_story_points(issue) == 1.0

    def test_parse_story_points_none(self):
        """
        Test that issue with story_points field as None defaults to 1.0
        """
        issue = {'story_points': None}
        assert _parse_story_points(issue) == 1.0

    def test_generate_burnout_basic(self):
        """
        Test that generate_burnout with basic input returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-01-01",
            "sprint_end": "2025-01-03",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-01-01", "closed_at": "2025-01-02", "story_points": 2},
                {"number": 2, "title": "two", "created_at": "2025-01-01", "closed_at": None, "labels": ["SP:3"]},
            ]
        }
        res = generate_burnout(input_json)
        assert len(res["actual"]) == 3
        assert len(res["ideal"]) == 3
        assert res["actual"][0]["remaining_points"] == 5.0
        assert res["actual"][-1]["remaining_points"] == 3.0  
        # Day 1: 5 points, Day 2: 3 points (one closed), Day 3: 3 points (no change)

    def test_generate_burnout_no_story_points(self):
        """
        Test that generate_burnout with issues lacking story_points info returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-02-01",
            "sprint_end": "2025-02-02",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-02-01", "closed_at": None},
                {"number": 2, "title": "two", "created_at": "2025-02-01", "closed_at": "2025-02-02"},
            ]
        }
        res = generate_burnout(input_json)
        assert res["actual"][0]["remaining_points"] == 2.0
        assert res["actual"][-1]["remaining_points"] == 1.0  

    def test_generate_burnout_no_closed_dates(self):
        """
        Test that generate_burnout with issues lacking closed_at info returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-03-01",
            "sprint_end": "2025-03-03",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-03-01", "closed_at": None, "story_points": 4},
                {"number": 2, "title": "two", "created_at": "2025-03-01", "closed_at": None, "labels": ["SP:2"]},
            ]
        }
        res = generate_burnout(input_json)
        assert res["actual"][0]["remaining_points"] == 6.0
        assert res["actual"][-1]["remaining_points"] == 6.0  # No issues closed, points remain the same

    def test_generate_burnout_all_closed(self):
        """ Test that generate_burnout with all issues closed returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-03-01",
            "sprint_end": "2025-03-03",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-03-01", "closed_at": "2025-03-02", "story_points": 4},
                {"number": 2, "title": "two", "created_at": "2025-03-01", "closed_at": "2025-03-03", "labels": ["SP:2"]},
            ]
        }
        res = generate_burnout(input_json)
        assert res["actual"][0]["remaining_points"] == 6.0
        assert res["actual"][-1]["remaining_points"] == 0.0  # Day 1: 6 points, Day 2: 2 points (one closed), Day 3: 0 points (all closed)
 
    def test_generate_burnout_all_open(self):
        """
        Test that generate_burnout with all issues open returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-04-01",
            "sprint_end": "2025-04-03",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-04-01", "closed_at": None, "story_points": 3},
                {"number": 2, "title": "two", "created_at": "2025-04-02", "closed_at": None, "labels": ["SP:4"]},
            ]
        }
        res = generate_burnout(input_json)
        assert res["actual"][0]["remaining_points"] == 3.0
        assert res["actual"][1]["remaining_points"] == 7.0
        assert res["actual"][2]["remaining_points"] == 7.0  # Day 1: 3 points, Day 2: 7 points (new issue), Day 3: 7 points (no change)

    def test_generate_burnout_no_issues(self):
        """
        Test that generate_burnout with no issues returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-04-01",
            "sprint_end": "2025-04-03",
            "issues": []
        }
        res = generate_burnout(input_json)
        assert all(x["remaining_points"] == 0.0 for x in res["actual"][1:])
    
    def test_generate_burnout_single_day(self):
        """
        Test that generate_burnout with single day sprint returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-06-15",
            "sprint_end": "2025-06-15",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-06-15", "closed_at": None, "story_points": 3},
            ]
        }
        res = generate_burnout(input_json)
        assert len(res["actual"]) == 1
        assert res["actual"][0]["remaining_points"] == 3.0
        assert len(res["ideal"]) == 1
        assert res["ideal"][0]["remaining_points"] == 3.0       

    def test_generate_burnout_start_equals_end(self):
        """
        Test that generate_burnout with sprint start equals end returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-07-20",
            "sprint_end": "2025-07-20",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-07-20", "closed_at": "2025-07-20", "story_points": 4},
                {"number": 2, "title": "two", "created_at": "2025-07-20", "closed_at": None, "labels": ["SP:2"]},
            ]
        }
        res = generate_burnout(input_json)
        assert len(res["actual"]) == 1
        assert res["actual"][0]["remaining_points"] == 2.0  # One closed on the same day, one remains
        assert len(res["ideal"]) == 1
        assert res["ideal"][0]["remaining_points"] == 6.0  # Total points at start
    
    def test_generate_burnout_all_closed_before_start(self):    
        """
        Test that generate_burnout with all issues closed before sprint start returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-04-01",
            "sprint_end": "2025-04-03",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-03-30", "closed_at": "2025-03-31", "story_points": 3},
                {"number": 2, "title": "two", "created_at": "2025-03-29", "closed_at": "2025-03-30", "labels": ["SP:4"]},
            ]
        }
        res = generate_burnout(input_json)
        assert all(x["remaining_points"] == 0.0 for x in res["actual"])

    def test_generate_burnout_all_created_after_end(self):
        """
        Test that generate_burnout with all issues created after sprint end returns correct calculation result
        """
        input_json = {
            "sprint_start": "2025-04-01",
            "sprint_end": "2025-04-03",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-04-04", "closed_at": None, "story_points": 3},
                {"number": 2, "title": "two", "created_at": "2025-04-05", "closed_at": None, "labels": ["SP:4"]},
            ]
        }
        res = generate_burnout(input_json)
        assert all(x["remaining_points"] == 0.0 for x in res["actual"])

    def test_generate_burnout_invalid_dates(self):
        """
        Test that generate_burnout with invalid date format raises ValueError
        """
        input_json = {
            "sprint_start": "2025/08/01",  # Invalid format
            "sprint_end": "2025-08-03",
            "issues": [
                {"number": 1, "title": "one", "created_at": "2025-08-01", "closed_at": None, "story_points": 3},
            ]
        }
        with pytest.raises(ValueError):
            generate_burnout(input_json)

