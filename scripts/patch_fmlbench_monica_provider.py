#!/usr/bin/env python3
"""Patch the official FML-bench repo to add a Monica OpenAI-compatible provider.

This modifies agents/llm.py in-place so the upstream benchmark can call
https://openapi.monica.im/v1 with MONICA_API_KEY.
"""

from __future__ import annotations

import argparse
from pathlib import Path


TARGET_SNIPPET = """provider_list = ['OpenRouter', 'Anthropic', 'AnthropicBedrock', 'AnthropicVertex', 'OpenAI', 'DeepSeek', 'Google']"""
REPLACEMENT_SNIPPET = """provider_list = ['OpenRouter', 'Anthropic', 'AnthropicBedrock', 'AnthropicVertex', 'OpenAI', 'DeepSeek', 'Google', 'Monica']"""


def patch_llm_py(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "provider == 'Monica'" in text:
        return False
    if TARGET_SNIPPET not in text:
        raise RuntimeError(f"Could not find provider list in {path}")

    text = text.replace(TARGET_SNIPPET, REPLACEMENT_SNIPPET, 1)

    anchor = """    elif provider == 'Google':
        print(f"Using Google Gemini (OpenAI-compatible) with model {model}.")
        return openai.OpenAI(
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ), model
    
    else:
        raise NotImplementedError(f"Provider {provider} not implemented.")
"""
    replacement = """    elif provider == 'Google':
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
    
    else:
        raise NotImplementedError(f"Provider {provider} not implemented.")
"""
    if anchor not in text:
        raise RuntimeError(f"Could not find insertion anchor in {path}")

    text = text.replace(anchor, replacement, 1)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Path to the cloned official FML-bench repo")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    llm_py = repo / "agents" / "llm.py"
    if not llm_py.exists():
        raise SystemExit(f"Missing file: {llm_py}")

    changed = patch_llm_py(llm_py)
    print("patched" if changed else "already patched")


if __name__ == "__main__":
    main()

