import datetime
import json
import os
import unittest
from core.pr_efficiency import collect_pr_data, _sum_pr_file_stats 

class DummyFile:
    def __init__(self, additions=None, deletions=None):
        self.additions = additions
        self.deletions = deletions

class DummyFullPR:
    def __init__(self, number, created_at=None, merged_at=None, state="open",
                 additions=None, deletions=None, changed_files=0, review_comments=0, files_list=None):
        self.number = number
        self.created_at = created_at
        self.merged_at = merged_at
        self.state = state
        self.additions = additions
        self.deletions = deletions
        self.changed_files = changed_files
        self.review_comments = review_comments
        self._files = files_list or []

    def files(self):
        return self._files

class DummyPRSummary:
    # returned by repository.pull_requests()
    def __init__(self, number):
        self.number = number

class DummyRepo:
    def __init__(self, full_prs):
        # full_prs: dict number -> DummyFullPR
        self._full_prs = full_prs

    def pull_requests(self, state="all"):
        # return list of summary objects
        return [DummyPRSummary(n) for n in self._full_prs.keys()]

    def pull_request(self, number):
        return self._full_prs[number]

class DummyGithubConn:
    def __init__(self, repos):
        # repos: dict (owner, repo) -> DummyRepo
        self._repos = repos

    def repository(self, owner, repo):
        key = (owner, repo)
        if key not in self._repos:
            raise Exception("repo not found")
        return self._repos[key]
    
class TestSumPRFileStats(unittest.TestCase):
    def test_sum_pr_file_stats_normal(self):
        # normal case with valid additions/deletions
        files = [DummyFile(additions=3, deletions=1), DummyFile(additions=2, deletions=4)]
        full_pr = DummyFullPR(number=42, files_list=files)
        a_sum, d_sum = _sum_pr_file_stats(full_pr)
        assert (a_sum, d_sum) == (5, 5)

    def test_sum_pr_file_stats_missing_values(self):
        # some files have None additions/deletions
        files = [DummyFile(additions=None, deletions=1), DummyFile(additions=2, deletions=None)]
        full_pr = DummyFullPR(number=43, files_list=files)
        a_sum, d_sum = _sum_pr_file_stats(full_pr)
        assert (a_sum, d_sum) == (2, 1)

    def test_sum_pr_file_stats_handles_exceptions(self):
        # construct a full_pr whose files() raises exception
        class BadPR:
            def __init__(self):
                self.number = 99
            def files(self):
                raise RuntimeError("boom")
        a_sum, d_sum = _sum_pr_file_stats(BadPR())
        assert (a_sum, d_sum) == (0, 0)

    def test_sum_pr_file_stats_no_files(self):
        # PR with no files changed
        full_pr = DummyFullPR(number=44, files_list=[])
        a_sum, d_sum = _sum_pr_file_stats(full_pr)
        assert (a_sum, d_sum) == (0, 0)

class TestCollectPRData:
    def test_collect_pr_data_basic(self,tmp_path):
        # contruct dummy data, two PRs, one with additions/deletions directly,
        # another with zero additions/deletions but files() returns data
        p1 = DummyFullPR(
            number=1,
            created_at=datetime.datetime(2023,1,1,12,0),
            merged_at=datetime.datetime(2023,1,2,12,0),
            state="closed",
            additions=10,
            deletions=2,
            changed_files=1,
            review_comments=3,
            files_list=[DummyFile(additions=10, deletions=2)]
        )
        p2 = DummyFullPR(
            number=2,
            created_at=datetime.datetime(2023,2,1,12,0),
            merged_at=None,
            state="open",
            additions=0,  # 
            deletions=0,
            changed_files=2,
            review_comments=1,
            files_list=[DummyFile(additions=5, deletions=1), DummyFile(additions=2, deletions=0)]
        )

        repo = DummyRepo({1: p1, 2: p2})
        gh = DummyGithubConn({("someowner", "somerepo"): repo})

        owners_and_repositories = [{"owner": "someowner", "repository": "somerepo"}]
        results = collect_pr_data(gh, owners_and_repositories)

        
        assert len(results) == 2
        r1 = next(r for r in results if r["id"] == "1")
        assert r1["additions"] == 10
        assert r1["deletions"] == 2
        assert r1["review_comments"] == 3
        assert r1["state"] == "closed"
        assert r1["created_at"] == "2023-01-01T12:00:00"

        r2 = next(r for r in results if r["id"] == "2")

        assert r2["additions"] == 7
        assert r2["deletions"] == 1
        assert r2["review_comments"] == 1

    def test_collect_pr_data_invalid_repo(self):
        # test handling of invalid repo info
        gh = DummyGithubConn({})
        owners_and_repositories = [{"owner": "invalidowner", "repository": "invalidrepo"}]
        results = collect_pr_data(gh, owners_and_repositories)
        assert len(results) == 0

    def test_collect_pr_data_partial_failure(self):
        # test handling of one valid and one invalid repo
        p1 = DummyFullPR(
            number=1,
            created_at=datetime.datetime(2023,1,1,12,0),
            merged_at=datetime.datetime(2023,1,2,12,0),
            state="closed",
            additions=10,
            deletions=2,
            changed_files=1,
            review_comments=3,
            files_list=[DummyFile(additions=10, deletions=2)]
        )
        repo = DummyRepo({1: p1})
        gh = DummyGithubConn({("validowner", "validrepo"): repo})

        owners_and_repositories = [
            {"owner": "validowner", "repository": "validrepo"},
            {"owner": "invalidowner", "repository": "invalidrepo"}
        ]
        results = collect_pr_data(gh, owners_and_repositories)
        assert len(results) == 1
        assert results[0]["id"] == "1"

    def test_collect_pr_data_handles_exceptions_in_pr_details(self):
        # test handling of exception when fetching PR details
        class BadRepo(DummyRepo):
            def pull_request(self, number):
                raise Exception("failed to fetch PR details")

        bad_repo = BadRepo({})
        gh = DummyGithubConn({("someowner", "somerepo"): bad_repo})

        owners_and_repositories = [{"owner": "someowner", "repository": "somerepo"}]
        results = collect_pr_data(gh, owners_and_repositories)
        assert len(results) == 0
    
    def test_collect_pr_data_no_prs(self):
        # test handling of repo with no PRs
        repo = DummyRepo({})
        gh = DummyGithubConn({("someowner", "somerepo"): repo}) 
        owners_and_repositories = [{"owner": "someowner", "repository": "somerepo"}]
        results = collect_pr_data(gh, owners_and_repositories)
        assert len(results) == 0


        # test handling of PRs with zero changed_files
        p1 = DummyFullPR(
            number=1,
            created_at=datetime.datetime(2023,1,1,12,0),
            merged_at=datetime.datetime(2023,1,2,12,0),
            state="closed",
            additions=0,
            deletions=0,
            changed_files=0,
            review_comments=0,
            files_list=[]
        )

        repo = DummyRepo({1: p1})
        gh = DummyGithubConn({("someowner", "somerepo"): repo})

        owners_and_repositories = [{"owner": "someowner", "repository": "somerepo"}]
        results = collect_pr_data(gh, owners_and_repositories)

        assert len(results) == 1
        r1 = results[0]
        assert r1["additions"] == 0
        assert r1["deletions"] == 0

    def test_collect_pr_data_merge_before_create(self):
        # test handling of PR where merged_at is before created_at
        p1 = DummyFullPR(
            number=1,
            created_at=datetime.datetime(2023,1,2,12,0),
            merged_at=datetime.datetime(2023,1,1,12,0),  # merged before created
            state="closed",
            additions=10,
            deletions=2,
            changed_files=1,
            review_comments=2,
            files_list=[DummyFile(additions=10, deletions=2)]
        )

        repo = DummyRepo({1: p1})
        gh = DummyGithubConn({("someowner", "somerepo"): repo})

        owners_and_repositories = [{"owner": "someowner", "repository": "somerepo"}]
        results = collect_pr_data(gh, owners_and_repositories)

        assert len(results) == 1
        r1 = results[0]
        assert r1["additions"] == 10
        assert r1["deletions"] == 2

