import unittest
import pytest  
from datetime import datetime  
from metrics.calculate_pr_review_efficiency import calculate_pr_review_efficiency  

def almost_eq(a, b, tol=1e-2):  
    return abs(a - b) <= tol  

class TestCalculatePRReviewEfficiency(unittest.TestCase):
    def test_single_pr_basic(self):  
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

    def test_multiple_prs_varied_data(self):
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
        assert "pr_details" in res and len(res["pr_details"]) == 2 
        for pr in res["pr_details"]:
            if pr["pr_id"] == "1":
                assert almost_eq(pr["merge_time_hours"], 2.00)
                assert almost_eq(pr["average_review_time_hours"], 1.00)
            elif pr["pr_id"] == "2":
                assert almost_eq(pr["merge_time_hours"], 6.00)
                assert almost_eq(pr["average_review_time_hours"], 1.50)

        assert "overall_statistics" in res
        overall = res["overall_statistics"]
        assert almost_eq(overall["average_efficiency_score"], 123.33)
        assert almost_eq(overall["average_merge_time_hours"], 4.0)
        assert almost_eq(overall["average_review_time_hours"], 1.75)

 



    def test_no_prs(self):
        # empty input
        input_data = []  
        res = calculate_pr_review_efficiency(input_data)  
        assert "pr_details" in res and len(res["pr_details"]) == 0

    def test_invalid_dates(self):
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

    def test_invalid_input_structure(self):
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

    def test_invalis_input(self):
        # input is not a list
        input_data = "invalid input"  
        with pytest.raises(Exception):
            calculate_pr_review_efficiency(input_data)

    def test_eq_created_merged(self):
        # PR where created_at == merged_at
        input_data = [  
            {  
                "id": "1",  
                "created_at": "2023-01-01T10:00:00Z",  
                "merged_at": "2023-01-01T10:00:00Z",  
                "state": "closed",  
                "additions": 100,  
                "deletions": 20,  
                "review_comments": 2  
            }  
        ]  
        res = calculate_pr_review_efficiency(input_data)  
        assert "pr_details" in res and len(res["pr_details"]) == 1  

        pr = res["pr_details"][0]  
        assert almost_eq(pr["merge_time_hours"], 0.00)  
        assert almost_eq(pr["average_review_time_hours"], 0.00)

    def test_zero_comment_merged_pr(self):
        # PR with zero review comments but merged
        input_data = [  
            {  
                "id": "1",  
                "created_at": "2023-01-01T10:00:00Z",  
                "merged_at": "2023-01-01T12:00:00Z",  
                "state": "closed",  
                "additions": 100,  
                "deletions": 20,  
                "review_comments": 0  
            }  
        ]  
        res = calculate_pr_review_efficiency(input_data)  
        assert "pr_details" in res and len(res["pr_details"]) == 1  

        pr = res["pr_details"][0]  
        assert almost_eq(pr["merge_time_hours"], 2.00)  
        assert almost_eq(pr["average_review_time_hours"], 2.00)  # treat as all time spent in review since no comments