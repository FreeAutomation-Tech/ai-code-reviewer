import os
import sys

from .github_client import GitHubClient
from .reviewer import review_diff


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def main():
    github_token = get_env("INPUT_GITHUB_TOKEN") or get_env("GITHUB_TOKEN")
    ai_provider = get_env("INPUT_AI_PROVIDER", "openai")
    model = get_env("INPUT_MODEL", "")
    openai_key = get_env("INPUT_OPENAI_API_KEY") or get_env("OPENAI_API_KEY", "")
    anthropic_key = get_env("INPUT_ANTHROPIC_API_KEY") or get_env("ANTHROPIC_API_KEY", "")
    ollama_endpoint = get_env("INPUT_OLLAMA_ENDPOINT", "http://localhost:11434")
    review_style = get_env("INPUT_REVIEW_STYLE", "constructive")
    max_comments_str = get_env("INPUT_MAX_COMMENTS", "10")
    exclude_paths = get_env(
        "INPUT_EXCLUDE_PATHS",
        "*.lock,*.min.js,*.min.css,*package-lock.json,*yarn.lock",
    )

    if not github_token:
        print("::error ::GITHUB_TOKEN is required")
        sys.exit(1)

    max_comments = int(max_comments_str)

    github_repository = get_env("GITHUB_REPOSITORY")
    pr_number_str = get_env("GITHUB_REF")
    if not github_repository:
        print("::error ::GITHUB_REPOSITORY is not set")
        sys.exit(1)

    pr_number = None
    if pr_number_str and "/pull/" in pr_number_str:
        try:
            pr_number = int(pr_number_str.split("/pull/")[1].split("/")[0])
        except (IndexError, ValueError):
            pass

    if not pr_number:
        event_path = get_env("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            import json
            with open(event_path) as f:
                event = json.load(f)
            pr_number = event.get("pull_request", {}).get("number")
            if not pr_number:
                issue = event.get("issue", {}).get("number")
                if issue:
                    pr_number = issue

    if not pr_number:
        print("::error ::Could not determine PR number from GITHUB_REF or GITHUB_EVENT_PATH")
        sys.exit(1)

    client = GitHubClient(github_token, github_repository)

    exclude_list = [p.strip() for p in exclude_paths.split(",") if p.strip()]

    print(f"::debug::Fetching diff for PR #{pr_number}")
    diff = client.get_pr_diff(pr_number)
    diff = client.filter_diff(diff, exclude_list)

    if not diff.strip():
        print("::notice ::No diff to review (all files may have been excluded)")
        sys.exit(0)

    api_key = ""
    if ai_provider == "openai":
        api_key = openai_key
    elif ai_provider == "anthropic":
        api_key = anthropic_key

    print(f"::debug::Reviewing with provider={ai_provider}, style={review_style}")
    try:
        review_text = review_diff(
            diff=diff,
            provider=ai_provider,
            api_key=api_key,
            model=model,
            style=review_style,
            ollama_endpoint=ollama_endpoint,
        )
    except Exception as e:
        print(f"::error ::AI review failed: {e}")
        sys.exit(1)

    if not review_text.strip():
        print("::notice ::AI returned empty review")
        sys.exit(0)

    comments = client.parse_review_comments(review_text)

    if not comments:
        summary = f"## AI Code Review\n\n{review_text}"
        client.post_review_comment(pr_number, summary)
        print(f"::notice ::Posted review summary to PR #{pr_number}")
        sys.exit(0)

    commit_sha = client.get_latest_commit_sha(pr_number)

    summary_lines = [f"## AI Code Review ({ai_provider})\n"]
    severity_counts = {"critical": 0, "major": 0, "minor": 0}
    for c in comments[:max_comments]:
        severity_counts[c["severity"]] = severity_counts.get(c["severity"], 0) + 1

    summary_lines.append(f"**Found {len(comments)} issues:** ")
    for sev, count in severity_counts.items():
        if count:
            summary_lines.append(f"- {sev}: {count}")
    summary_lines.append("\n")

    posted_inline = 0
    for comment in comments:
        if posted_inline >= max_comments:
            break
        file_path = comment["file"]
        line = comment["line"]
        text = comment["text"]
        if file_path and line and text:
            try:
                client.post_inline_comment(pr_number, text, commit_sha, file_path, line)
                posted_inline += 1
            except Exception as e:
                print(f"::warning ::Failed to post inline comment on {file_path}:{line}: {e}")
                summary_lines.append(f"\n**{file_path}:{line}** ({comment['severity']}):\n{text}")

    if posted_inline < len(comments):
        remaining = comments[posted_inline:]
        for c in remaining:
            summary_lines.append(f"\n**{c['file']}:{c['line']}** ({c['severity']}):\n{c['text']}")

    summary = "\n".join(summary_lines)
    client.post_review_comment(pr_number, summary)
    print(f"::notice ::Posted {posted_inline} inline comments and summary to PR #{pr_number}")


if __name__ == "__main__":
    main()
