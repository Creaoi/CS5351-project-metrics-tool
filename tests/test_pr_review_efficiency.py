import unittest
import pytest  
from datetime import datetime  
from metrics.calculate_pr_review_efficiency import calculate_pr_review_efficiency  

def almost_eq(a, b, tol=1e-2):  
    return abs(a - b) <= tol  

class TestCalculatePRReviewEfficiency(unittest.TestCase):
    def test_single_pr_basic():  
        # single PR with known data
        input_data = [  
            {  
                "id": "1",  
                "created_at": "2023-01-01T10:00:00Z",  
                "merged_at": "2023-01-01T12:00:00Z",  
                "state": "closed",  
                "additions": 150,  
                "deletions": 50,  
                "review_comments": 2  
            }  
        ]  
        res = calculate_pr_review_efficiency(input_data)  
        assert "pr_details" in res and len(res["pr_details"]) == 1  

        pr = res["pr_details"][0]  
        # merge_time = 2 hours  
        assert almost_eq(pr["merge_time_hours"], 2.00)  
        # review_count = 2 -> average_review_time = 1 hour  
        assert almost_eq(pr["average_review_time_hours"], 1.00)  

    def test_multiple_prs_varied_data():
        # multiple PRs with varied data, including unmerged PR, open PR and zero review comment PR
        input_data = [  
            {  
                "id": "1",  
                "created_at": "2023-01-01T10:00:00Z",  
                "merged_at": "2023-01-01T12:00:00Z",  
                "state": "closed",  
                "additions": 100,  
                "deletions": 20,  
                "review_comments": 1  
            },  
            {  
                "id": "2",  
                "created_at": "2023-01-02T09:00:00Z",  
                "merged_at": "2023-01-02T15:00:00Z",  
                "state": "closed",  
                "additions": 200,  
                "deletions": 80,  
                "review_comments": 4  
            },  
            {  
                "id": "3",  
                "created_at": "2023-01-03T08:00:00Z",  
                "merged_at": None,  # not merged yet  
                "state": "open",  
                "additions": 50,  
                "deletions": 10,  
                "review_comments": 0  
            }  
        ]  
        res = calculate_pr_review_efficiency(input_data)  
        assert "pr_details" in res and len(res["pr_details"]) == 3  

        pr1 = next(pr for pr in res["pr_details"] if pr["id"] == "1")  
        assert almost_eq(pr1["merge_time_hours"], 2.00)  
        assert almost_eq(pr1["average_review_time_hours"], 2.00)  

        pr2 = next(pr for pr in res["pr_details"] if pr["id"] == "2")  
        assert almost_eq(pr2["merge_time_hours"], 6.00)  
        assert almost_eq(pr2["average_review_time_hours"], 1.50)  

        pr3 = next(pr for pr in res["pr_details"] if pr["id"] == "3")  
        assert pr3["merge_time_hours"] is None  
        assert pr3["average_review_time_hours"] is None

    def test_no_prs():
        # empty input
        input_data = []  
        res = calculate_pr_review_efficiency(input_data)  
        assert "pr_details" in res and len(res["pr_details"]) == 0

    def test_invalid_dates():
        # PRs with invalid date formats
        input_data = [  
            {  
                "id": "1",  
                "created_at": "invalid-date",  
                "merged_at": "2023-01-01T12:00:00Z",  
                "state": "closed",  
                "additions": 100,  
                "deletions": 20,  
                "review_comments": 1  
            }  
        ]  
        res = calculate_pr_review_efficiency(input_data)  
        assert "pr_details" in res and len(res["pr_details"]) == 1  

        pr = res["pr_details"][0]  
        assert pr["merge_time_hours"] is None  
        assert pr["average_review_time_hours"] is None

    def test_invalid_input_structure():
        # input with missing fields
        input_data = [  
            {  
                "id": "1",  
                # missing created_at  
                "merged_at": "2023-01-01T12:00:00Z",  
                "state": "closed",  
                "additions": 100,  
                "deletions": 20,  
                "review_comments": 1  
            }  
        ]  
        res = calculate_pr_review_efficiency(input_data)  
        assert "pr_details" in res and len(res["pr_details"]) == 1  

        pr = res["pr_details"][0]  
        assert pr["merge_time_hours"] is None  
        assert pr["average_review_time_hours"] is None

    def test_invalis_input():
        # input is not a list
        input_data = "invalid input"  
        with pytest.raises(Exception):
            calculate_pr_review_efficiency(input_data)