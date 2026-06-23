import os
import fnmatch
from github import Github, GithubIntegration
from github.PullRequest import PullRequest


class GitHubClient:
    def __init__(self, token: str, repo_name: str):
        self.client = Github(token)
        self.repo = self.client.get_repo(repo_name)

    def get_pr(self, pr_number: int) -> PullRequest:
        return self.repo.get_pull(pr_number)

    def get_pr_diff(self, pr_number: int) -> str:
        pr = self.get_pr(pr_number)
        files = pr.get_files()
        diff_parts = []
        for f in files:
            if f.patch:
                diff_parts.append(f"--- a/{f.filename}\n+++ b/{f.filename}\n{f.patch}")
        return "\n".join(diff_parts)

    def get_changed_files(self, pr_number: int):
        pr = self.get_pr(pr_number)
        return list(pr.get_files())

    def file_matches(self, filename: str, patterns: list[str]) -> bool:
        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern.strip()):
                return True
        return False

    def filter_diff(self, diff: str, exclude_patterns: list[str]) -> str:
        if not exclude_patterns:
            return diff
        lines = diff.split("\n")
        filtered = []
        skip_file = False
        for line in lines:
            if line.startswith("--- a/"):
                fname = line[6:]
                skip_file = self.file_matches(fname, exclude_patterns)
            if not skip_file:
                filtered.append(line)
        return "\n".join(filtered)

    def post_review_comment(self, pr_number: int, body: str):
        pr = self.get_pr(pr_number)
        pr.create_issue_comment(body)

    def post_inline_comment(self, pr_number: int, body: str, commit_id: str, path: str, line: int):
        pr = self.get_pr(pr_number)
        pr.create_review_comment(body=body, commit=commit_id, path=path, line=line)

    def get_latest_commit_sha(self, pr_number: int) -> str:
        pr = self.get_pr(pr_number)
        return pr.head.sha

    def parse_review_comments(self, review_text: str):
        comments = []
        current_comment = {"file": "", "line": 0, "severity": "minor", "text": ""}
        for line in review_text.strip().split("\n"):
            if line.startswith("FILE:"):
                if current_comment["text"]:
                    comments.append(current_comment)
                    current_comment = {"file": "", "line": 0, "severity": "minor", "text": ""}
                parts = line.split(" LINE:")
                current_comment["file"] = parts[0].replace("FILE:", "").strip()
                if len(parts) > 1:
                    rest = parts[1].split(" SEVERITY:")
                    current_comment["line"] = int(rest[0].strip())
                    if len(rest) > 1:
                        current_comment["severity"] = rest[1].strip().lower()
            else:
                if current_comment["text"]:
                    current_comment["text"] += "\n" + line
                else:
                    current_comment["text"] = line
        if current_comment["text"]:
            comments.append(current_comment)
        return comments
