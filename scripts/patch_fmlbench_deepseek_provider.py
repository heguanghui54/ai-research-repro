#!/usr/bin/env python3
"""Patch the official FML-bench repo to add a DeepSeek provider.

The upstream repo already knows how to call DeepSeek-style models, but its
provider switch does not create a DeepSeek client. This script inserts a tiny
OpenAI-compatible DeepSeek branch so the benchmark can be run with a
DEEPSEEK_API_KEY and the standard DeepSeek base URL.
"""

from __future__ import annotations

import argparse
from pathlib import Path


TARGET_OLD = """    elif provider == 'Google':
        print(f"Using Google Gemini (OpenAI-compatible) with model {model}.")
        return openai.OpenAI(
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ), model

    elif provider == 'Monica':
        print(f"Using Monica API with model {model}.")
        return openai.OpenAI(
            api_key=os.environ["MONICA_API_KEY"],
            base_url=os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1")
        ), model
"""


TARGET_NEW = """    elif provider == 'Google':
        print(f"Using Google Gemini (OpenAI-compatible) with model {model}.")
        return openai.OpenAI(
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ), model

    elif provider == 'DeepSeek':
        print(f"Using DeepSeek API with model {model}.")
        return openai.OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        ), model

    elif provider == 'Monica':
        print(f"Using Monica API with model {model}.")
        return openai.OpenAI(
            api_key=os.environ["MONICA_API_KEY"],
            base_url=os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1")
        ), model
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Path to the FML-bench repo root")
    args = parser.parse_args()

    path = Path(args.repo) / "agents" / "llm.py"
    text = path.read_text()
    if TARGET_NEW in text:
        print(f"DeepSeek provider already present in {path}")
        return
    if TARGET_OLD not in text:
        raise SystemExit(f"Target block not found in {path}")
    path.write_text(text.replace(TARGET_OLD, TARGET_NEW))
    print(f"Patched {path}")


if __name__ == "__main__":
    main()
