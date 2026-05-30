from __future__ import annotations

import json
import os
import re
import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


@dataclass
class LLMResult:
    text: str
    parsed: Any | None = None
    meta: dict[str, Any] | None = None


@dataclass
class LLMProvider:
    api_key: str
    base_url: str | None = None
    name: str = "openai"


def _load_local_env() -> None:
    candidates = []
    if os.getenv("AI_RESEARCH_ENV_FILE"):
        candidates.append(Path(os.environ["AI_RESEARCH_ENV_FILE"]).expanduser())
    candidates.extend(
        [
            Path.cwd() / ".env",
            Path.cwd().parent / ".env",
            Path.home() / ".config" / "ai_research_repro" / ".env",
        ]
    )
    for env_path in candidates:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and not os.environ.get(key):
                os.environ[key] = value


def _resolve_provider(model: str, *, multimodal: bool = False) -> LLMProvider | None:
    """Resolve an OpenAI-compatible provider.

    Preference order follows the research plan: DeepSeek for normal text/code
    calls, Monica-compatible multimodal routing for VLM calls, then OpenAI.
    """
    _load_local_env()
    if multimodal:
        if os.getenv("MONICA_API_KEY"):
            return LLMProvider(
                api_key=os.environ["MONICA_API_KEY"],
                base_url=os.getenv("MONICA_BASE_URL", "https://openapi.monica.im/v1"),
                name="monica",
            )
        if os.getenv("OPENAI_API_KEY"):
            return LLMProvider(
                api_key=os.environ["OPENAI_API_KEY"],
                base_url=os.getenv("OPENAI_BASE_URL"),
                name="openai",
            )
        return None
    monica_text_prefixes = tuple(
        item.strip()
        for item in os.getenv("MONICA_TEXT_MODEL_PREFIXES", "gpt-,o1,o3,o4,monica:").split(",")
        if item.strip()
    )
    if os.getenv("MONICA_API_KEY") and any(model.startswith(prefix) for prefix in monica_text_prefixes):
        return LLMProvider(
            api_key=os.environ["MONICA_API_KEY"],
            base_url=os.getenv("MONICA_BASE_URL", "https://openapi.monica.im/v1"),
            name="monica",
        )
    if os.getenv("DEEPSEEK_API_KEY"):
        return LLMProvider(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            name="deepseek",
        )
    if os.getenv("OPENAI_API_KEY"):
        return LLMProvider(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.getenv("OPENAI_BASE_URL"),
            name="openai",
        )
    return None


def provider_status() -> dict[str, Any]:
    _load_local_env()
    text_provider = _resolve_provider(os.getenv("DEEPSEEK_MODEL", "deepseek-chat"), multimodal=False)
    vlm_provider = _resolve_provider(os.getenv("MONICA_VLM_MODEL", "gpt-4o"), multimodal=True)
    hint = ""
    if not text_provider:
        hint = "No exported DEEPSEEK_API_KEY was visible. In Codex environment setup scripts, use `export DEEPSEEK_API_KEY=...` or write a .env file."
    return {
        "text_provider": text_provider.name if text_provider else "fallback",
        "text_model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat") if text_provider else "",
        "text_has_key": bool(text_provider),
        "text_base_url": text_provider.base_url if text_provider else "",
        "vlm_provider": vlm_provider.name if vlm_provider else "fallback",
        "vlm_model": os.getenv("MONICA_VLM_MODEL", "gpt-4o") if vlm_provider else "",
        "vlm_has_key": bool(vlm_provider),
        "vlm_base_url": vlm_provider.base_url if vlm_provider else "",
        "hint": hint,
    }


def _extract_json(text: str) -> Any:
    candidate = text.strip()
    match = _JSON_BLOCK_RE.search(candidate)
    if match:
        candidate = match.group(1).strip()
    return json.loads(candidate)


def _fallback_json(fallback: Callable[[], Any]) -> Any:
    return fallback()


def _usage_dict(resp: Any) -> dict[str, int]:
    usage = getattr(resp, "usage", None)
    if usage is None:
        return {}
    return {
        "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
        "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
    }


def _api_timeout_seconds() -> float:
    raw = os.getenv("AI_RESEARCH_API_TIMEOUT_SECONDS", "45")
    try:
        return max(5.0, float(raw))
    except ValueError:
        return 45.0


def chat_text(
    *,
    system: str,
    user: str,
    model: str = "gpt-4o-mini",
    fallback: Callable[[], str] | None = None,
    multimodal: bool = False,
) -> LLMResult:
    provider = _resolve_provider(model, multimodal=multimodal)
    if provider:
        try:
            from openai import OpenAI

            kwargs: dict[str, Any] = {
                "api_key": provider.api_key,
                "timeout": _api_timeout_seconds(),
                "max_retries": 2,
            }
            if provider.base_url:
                kwargs["base_url"] = provider.base_url
            client = OpenAI(**kwargs)
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
            )
            text = resp.choices[0].message.content or ""
            return LLMResult(
                text=text,
                meta={
                    "provider": provider.name,
                    "model": model,
                    "fallback": False,
                    "usage": _usage_dict(resp),
                },
            )
        except Exception as exc:  # pragma: no cover - network dependent
            if fallback is None:
                raise
            return LLMResult(
                text=fallback(),
                parsed={"provider": provider.name, "warning": str(exc)},
                meta={"provider": provider.name, "model": model, "fallback": True, "warning": str(exc), "usage": {}},
            )
    if fallback is None:
        raise RuntimeError("No LLM API key is set and no fallback was provided.")
    return LLMResult(text=fallback(), meta={"provider": "fallback", "model": model, "fallback": True, "usage": {}})


def chat_json(
    *,
    system: str,
    user: str,
    model: str = "gpt-4o-mini",
    fallback: Callable[[], Any] | None = None,
    multimodal: bool = False,
) -> Any:
    return chat_json_result(
        system=system,
        user=user,
        model=model,
        fallback=fallback,
        multimodal=multimodal,
    ).parsed


def chat_json_result(
    *,
    system: str,
    user: str,
    model: str = "gpt-4o-mini",
    fallback: Callable[[], Any] | None = None,
    multimodal: bool = False,
) -> LLMResult:
    result = chat_text(
        system=system,
        user=user,
        model=model,
        fallback=None if fallback is None else lambda: json.dumps(fallback()),
        multimodal=multimodal,
    )
    try:
        result.parsed = _extract_json(result.text)
        return result
    except Exception:
        if fallback is not None:
            result.parsed = _fallback_json(fallback)
            if result.meta is None:
                result.meta = {}
            result.meta["fallback"] = True
            result.meta["json_parse_fallback"] = True
            return result
        raise


def chat_vision_text(
    *,
    system: str,
    user: str,
    image_paths: list[Path],
    model: str | None = None,
    fallback: Callable[[], str] | None = None,
) -> LLMResult:
    _load_local_env()
    model = model or os.getenv("MONICA_VLM_MODEL", "gpt-4o")
    provider = _resolve_provider(model, multimodal=True)
    if provider:
        try:
            from openai import OpenAI

            kwargs: dict[str, Any] = {
                "api_key": provider.api_key,
                "timeout": _api_timeout_seconds(),
                "max_retries": 2,
            }
            if provider.base_url:
                kwargs["base_url"] = provider.base_url
            client = OpenAI(**kwargs)
            content: list[dict[str, Any]] = [{"type": "text", "text": user}]
            for image_path in image_paths:
                mime_type = mimetypes.guess_type(str(image_path))[0] or "image/png"
                data = base64.b64encode(image_path.read_bytes()).decode("ascii")
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{data}"},
                    }
                )
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": content},
                ],
                temperature=0.1,
            )
            return LLMResult(
                text=resp.choices[0].message.content or "",
                meta={
                    "provider": provider.name,
                    "model": model,
                    "fallback": False,
                    "usage": _usage_dict(resp),
                },
            )
        except Exception as exc:  # pragma: no cover - network dependent
            if fallback is None:
                raise
            return LLMResult(
                text=fallback(),
                parsed={"provider": provider.name, "warning": str(exc)},
                meta={"provider": provider.name, "model": model, "fallback": True, "warning": str(exc), "usage": {}},
            )
    if fallback is None:
        raise RuntimeError("No multimodal LLM API key is set and no fallback was provided.")
    return LLMResult(text=fallback(), meta={"provider": "fallback", "model": model, "fallback": True, "usage": {}})
