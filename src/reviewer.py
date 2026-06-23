import os
from typing import Optional

from .prompts import get_system_prompt


def openai_review(diff: str, model: str, api_key: str, style: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    model_name = model or "gpt-4"
    system_prompt = get_system_prompt(style)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review this pull request diff:\n\n{diff}"},
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""


def anthropic_review(diff: str, model: str, api_key: str, style: str) -> str:
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    model_name = model or "claude-3-opus-20240229"
    system_prompt = get_system_prompt(style)
    response = client.messages.create(
        model=model_name,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Review this pull request diff:\n\n{diff}"},
        ],
        max_tokens=2000,
        temperature=0.3,
    )
    return response.content[0].text if response.content else ""


def ollama_review(diff: str, model: str, endpoint: str, style: str) -> str:
    import requests
    model_name = model or "codellama"
    system_prompt = get_system_prompt(style)
    response = requests.post(
        f"{endpoint}/api/chat",
        json={
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Review this pull request diff:\n\n{diff}"},
            ],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def review_diff(
    diff: str,
    provider: str,
    api_key: Optional[str],
    model: str,
    style: str,
    ollama_endpoint: str = "http://localhost:11434",
) -> str:
    if provider == "openai":
        if not api_key:
            raise ValueError("OpenAI API key is required")
        return openai_review(diff, model, api_key, style)
    elif provider == "anthropic":
        if not api_key:
            raise ValueError("Anthropic API key is required")
        return anthropic_review(diff, model, api_key, style)
    elif provider == "ollama":
        return ollama_review(diff, model, ollama_endpoint, style)
    else:
        raise ValueError(f"Unknown provider: {provider}. Use openai, anthropic, or ollama.")
