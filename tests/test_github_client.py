from src.github_client import GitHubClient


class TestFileMatching:
    def setup_method(self):
        self.client = GitHubClient.__new__(GitHubClient)

    def test_file_matches_basic(self):
        assert self.client.file_matches("package-lock.json", ["*package-lock.json"])
        assert self.client.file_matches("dist/bundle.min.js", ["*.min.js"])
        assert not self.client.file_matches("src/app.py", ["*.min.js"])

    def test_file_matches_multiple_patterns(self):
        patterns = ["*.lock", "*.min.js", "*.min.css"]
        assert self.client.file_matches("yarn.lock", patterns)
        assert self.client.file_matches("style.min.css", patterns)
        assert not self.client.file_matches("main.py", patterns)


class TestParseReviewComments:
    def setup_method(self):
        self.client = GitHubClient.__new__(GitHubClient)

    def test_parse_single_comment(self):
        text = """FILE:src/main.py LINE:42 SEVERITY:critical
This is a security issue. Use parameterized queries."""
        comments = self.client.parse_review_comments(text)
        assert len(comments) == 1
        assert comments[0]["file"] == "src/main.py"
        assert comments[0]["line"] == 42
        assert comments[0]["severity"] == "critical"

    def test_parse_multiple_comments(self):
        text = """FILE:src/app.py LINE:10 SEVERITY:major
Use async/await here.
FILE:src/utils.py LINE:25 SEVERITY:minor
Consider adding a docstring."""
        comments = self.client.parse_review_comments(text)
        assert len(comments) == 2
        assert comments[0]["file"] == "src/app.py"
        assert comments[1]["severity"] == "minor"

    def test_parse_no_file_prefix(self):
        text = """This is a general comment about the PR."""
        comments = self.client.parse_review_comments(text)
        assert len(comments) == 1
        assert comments[0]["file"] == ""

    def test_parse_empty_text(self):
        comments = self.client.parse_review_comments("")
        assert comments == []

    def test_parse_multiline_comment_body(self):
        text = """FILE:src/main.py LINE:5 SEVERITY:major
Line 1 of comment.
Line 2 of comment."""
        comments = self.client.parse_review_comments(text)
        assert len(comments) == 1
        assert "Line 1" in comments[0]["text"]
        assert "Line 2" in comments[0]["text"]


class TestFilterDiff:
    def setup_method(self):
        self.client = GitHubClient.__new__(GitHubClient)

    def test_filter_excludes_matching_file(self):
        diff = """--- a/package-lock.json
+++ b/package-lock.json
@@ -1,5 +1,6 @@
-old
+new
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,4 @@
-old
+new"""
        result = self.client.filter_diff(diff, ["*package-lock.json"])
        assert "package-lock.json" not in result
        assert "src/main.py" in result

    def test_no_exclude_patterns(self):
        diff = "--- a/src/main.py\n+++ b/src/main.py\n@@ -1 +1 @@\n-old\n+new"
        result = self.client.filter_diff(diff, [])
        assert result == diff
