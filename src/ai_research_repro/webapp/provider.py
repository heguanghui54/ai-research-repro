from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

import httpx


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _extract_json(text: str) -> Any:
    candidate = text.strip()
    match = _JSON_BLOCK_RE.search(candidate)
    if match:
        candidate = match.group(1).strip()
    return json.loads(candidate)


@dataclass
class ProviderConfig:
    base_url: str
    api_key: str | None
    model: str
    name: str = "openai-compatible"


class OpenAICompatibleProvider:
    def __init__(self, config: ProviderConfig):
        self.config = config

    @property
    def available(self) -> bool:
        return bool(self.config.api_key)

    def _request(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        if not self.config.api_key:
            raise RuntimeError("API key is not configured for this project.")
        base_url = self.config.base_url.rstrip("/")
        url = f"{base_url}/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
        }
        with httpx.Client(timeout=180) as client:
            response = client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"] or ""

    def complete_text(self, *, system: str, user: str, fallback: Callable[[], str] | None = None) -> str:
        try:
            return self._request(
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ]
            )
        except Exception:
            if fallback is None:
                raise
            return fallback()

    def complete_json(self, *, system: str, user: str, fallback: Callable[[], Any] | None = None) -> Any:
        text = self.complete_text(system=system, user=user, fallback=None if fallback is None else lambda: json.dumps(fallback()))
        try:
            return _extract_json(text)
        except Exception:
            if fallback is None:
                raise
            return fallback()

