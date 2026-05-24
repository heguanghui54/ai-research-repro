from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


@dataclass
class LLMResult:
    text: str
    parsed: Any | None = None


def _extract_json(text: str) -> Any:
    candidate = text.strip()
    match = _JSON_BLOCK_RE.search(candidate)
    if match:
        candidate = match.group(1).strip()
    return json.loads(candidate)


def _fallback_json(fallback: Callable[[], Any]) -> Any:
    return fallback()


def chat_text(
    *,
    system: str,
    user: str,
    model: str = "gpt-4o-mini",
    fallback: Callable[[], str] | None = None,
) -> LLMResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )
            text = resp.choices[0].message.content or ""
            return LLMResult(text=text)
        except Exception as exc:  # pragma: no cover - network dependent
            if fallback is None:
                raise
            return LLMResult(text=fallback(), parsed={"warning": str(exc)})
    if fallback is None:
        raise RuntimeError("OPENAI_API_KEY is not set and no fallback was provided.")
    return LLMResult(text=fallback())


def chat_json(
    *,
    system: str,
    user: str,
    model: str = "gpt-4o-mini",
    fallback: Callable[[], Any] | None = None,
) -> Any:
    result = chat_text(system=system, user=user, model=model, fallback=None if fallback is None else lambda: json.dumps(fallback()))
    try:
        return _extract_json(result.text)
    except Exception:
        if fallback is not None:
            return _fallback_json(fallback)
        raise

