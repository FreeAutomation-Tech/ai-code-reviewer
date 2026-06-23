# AI Code Reviewer

[![Test](https://github.com/FreeAutomation-Tech/ai-code-reviewer/actions/workflows/test.yml/badge.svg)](https://github.com/FreeAutomation-Tech/ai-code-reviewer/actions/workflows/test.yml)
[![Docker Build](https://github.com/FreeAutomation-Tech/ai-code-reviewer/actions/workflows/docker-test.yml/badge.svg)](https://github.com/FreeAutomation-Tech/ai-code-reviewer/actions/workflows/docker-test.yml)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-AI%20Code%20Reviewer-purple?logo=github)](https://github.com/marketplace)

**Automatically review Pull Requests using AI** — supports OpenAI (GPT-4), Anthropic (Claude), and Ollama (local models). Drop it into any repo and get instant, actionable code reviews on every PR.

---

## Features

-   Multi-provider AI: OpenAI, Anthropic, or Ollama
-   Inline PR comments on specific lines
-   3 review styles: constructive, strict, concise
-   Smart file exclusion (`.lock`, `min.js`, etc.)
-   Configurable max comments per review
-   Zero-config setup — add to any repo in 30 seconds

---

## Quick Start

Add this workflow to `.github/workflows/ai-review.yml` in your repo:

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: FreeAutomation-Tech/ai-code-reviewer@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

That's it. Every PR will now get an AI review.

---

## Configuration

| Input | Required | Default | Description |
|---|---|---|---|
| `github_token` | Yes | — | `${{ secrets.GITHUB_TOKEN }}` |
| `ai_provider` | No | `openai` | `openai`, `anthropic`, or `ollama` |
| `model` | No | provider default | e.g. `gpt-4`, `claude-3-opus-20240229`, `codellama` |
| `openai_api_key` | No* | — | OpenAI API key |
| `anthropic_api_key` | No* | — | Anthropic API key |
| `ollama_endpoint` | No | `http://localhost:11434` | Ollama server URL |
| `review_style` | No | `constructive` | `constructive`, `strict`, or `concise` |
| `max_comments` | No | `10` | Max inline comments to post |
| `exclude_paths` | No | `*.lock,*.min.js,...` | Glob patterns to skip |

*\*Required when `ai_provider` matches.*

---

## Examples

### OpenAI (GPT-4)

```yaml
- uses: FreeAutomation-Tech/ai-code-reviewer@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    ai_provider: openai
    model: gpt-4
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    review_style: strict
```

### Anthropic (Claude)

```yaml
- uses: FreeAutomation-Tech/ai-code-reviewer@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    ai_provider: anthropic
    model: claude-3-opus-20240229
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Ollama (Local)

```yaml
- uses: FreeAutomation-Tech/ai-code-reviewer@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    ai_provider: ollama
    model: codellama
    ollama_endpoint: http://localhost:11434
```

### Concise, low-noise reviews

```yaml
- uses: FreeAutomation-Tech/ai-code-reviewer@v1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    review_style: concise
    max_comments: 5
```

---

## What It Looks Like

```
┌─────────────────────────────────────────────────────────┐
│  ## AI Code Review (openai)                             │
│                                                         │
│  **Found 3 issues:**                                    │
│  - critical: 1                                          │
│  - major: 1                                             │
│  - minor: 1                                             │
│                                                         │
│  ## src/db.py:15 (critical)                             │
│  SQL injection risk: use parameterized queries instead  │
│  of f-string interpolation.                             │
│                                                         │
│  ## src/api.py:42 (major)                               │
│  Missing error handling for network timeouts.           │
│                                                         │
│  ## src/utils.py:8 (minor)                              │
│  Unused import `os`.                                    │
└─────────────────────────────────────────────────────────┘
```

The action posts inline comments on the relevant lines **and** a summary comment on the PR. You get the full picture in one place.

---

## Development

```bash
# Clone
git clone https://github.com/FreeAutomation-Tech/ai-code-reviewer.git
cd ai-code-reviewer

# Install deps
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Build Docker image
docker build -t ai-code-reviewer .
```

---

## Why AI Code Review?

-   **Catches bugs early** — before they reach production
-   **Consistent standards** — every PR gets the same thorough review
-   **Saves maintainer time** — focus on architectural decisions, not style nits
-   **Works 24/7** — review happens automatically on every push

---

## License

MIT
