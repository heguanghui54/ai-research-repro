from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

_PROVIDER_DEFAULTS = {
    "deepseek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-v4-flash",
    },
    "monica": {
        "api_key_env": "MONICA_API_KEY",
        "base_url": "https://openapi.monica.im/v1",
        "default_model": "gpt-4o-mini",
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "default_model": "gpt-4o-mini",
    },
}

_PROVIDER_ALIASES = {
    "deepseek": "deepseek",
    "deepseek-api": "deepseek",
    "monica": "monica",
    "monica-api": "monica",
    "openai": "openai",
    "auto": "auto",
    None: "auto",
}


@dataclass
class LLMResult:
    text: str
    parsed: Any | None = None


@dataclass
class ProviderConfig:
    provider: str
    api_key: str
    base_url: str | None
    model: str


def _normalize_provider(provider: str | None) -> str:
    return _PROVIDER_ALIASES.get(provider, provider or "auto")


def _resolve_provider_config(
    *,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> ProviderConfig | None:
    normalized = _normalize_provider(provider)
    provider_order = ["deepseek", "monica", "openai"] if normalized == "auto" else [normalized]
    for name in provider_order:
        defaults = _PROVIDER_DEFAULTS.get(name)
        if defaults is None:
            continue
        resolved_key = api_key or os.getenv(defaults["api_key_env"])
        if not resolved_key:
            continue
        resolved_base = base_url if base_url is not None else defaults["base_url"]
        resolved_model = model or defaults["default_model"]
        return ProviderConfig(
            provider=name,
            api_key=resolved_key,
            base_url=resolved_base,
            model=resolved_model,
        )
    return None


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
    model: str | None = None,
    provider: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    fallback: Callable[[], str] | None = None,
) -> LLMResult:
    provider_config = _resolve_provider_config(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )
    if provider_config:
        try:
            from openai import OpenAI

            client_kwargs = {"api_key": provider_config.api_key}
            if provider_config.base_url:
                client_kwargs["base_url"] = provider_config.base_url
            client = OpenAI(**client_kwargs)
            resp = client.chat.completions.create(
                model=provider_config.model,
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
    model: str | None = None,
    provider: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    fallback: Callable[[], Any] | None = None,
) -> Any:
    result = chat_text(
        system=system,
        user=user,
        model=model,
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        fallback=None if fallback is None else lambda: json.dumps(fallback()),
    )
    try:
        return _extract_json(result.text)
    except Exception:
        if fallback is not None:
            return _fallback_json(fallback)
        raise
