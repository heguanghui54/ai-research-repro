#!/usr/bin/env python3
"""Run a direct LLM rewrite baseline for an arbitrary Python evaluator.

The evaluator file must expose evaluate(path: str) -> dict. The model receives
the initial program, evaluator context, public API signature, and task
description, then returns a complete Python file.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any

from openai import OpenAI


def _load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location("direct_program_evaluator", path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"Could not load evaluator from {path}")
    spec.loader.exec_module(module)
    if not hasattr(module, "evaluate"):
        raise RuntimeError(f"Evaluator {path} does not define evaluate(path)")
    return module.evaluate


def _extract_python_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + "\n"
    return text.strip() + "\n"


def _provider_config(provider: str, model: str | None) -> tuple[str, str, str]:
    provider = provider.lower()
    if provider == "monica":
        return (
            os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1"),
            os.environ["MONICA_API_KEY"],
            model or "gpt-4o-mini",
        )
    if provider == "deepseek":
        return (
            os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            os.environ["DEEPSEEK_API_KEY"],
            model or "deepseek-chat",
        )
    return (
        os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        os.environ["OPENAI_API_KEY"],
        model or "gpt-4o-mini",
    )


def _jsonable(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run direct LLM program rewrite baseline.")
    parser.add_argument("--initial-program", required=True)
    parser.add_argument("--evaluator", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--signature", required=True)
    parser.add_argument("--task-description", required=True)
    parser.add_argument("--provider", default="deepseek", choices=["deepseek", "monica", "openai"])
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    initial_path = Path(args.initial_program)
    evaluator_path = Path(args.evaluator)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    api_base, api_key, model = _provider_config(args.provider, args.model)
    initial_code = initial_path.read_text(encoding="utf-8")
    evaluator_code = evaluator_path.read_text(encoding="utf-8")

    prompt = f"""Rewrite the Python program to maximize the evaluator score.

Return only a complete Python file. Preserve this public API exactly:

{args.signature}

Task:
{args.task_description}

Initial program:
```python
{initial_code}
```

Evaluator context:
```python
{evaluator_code}
```
"""

    client = OpenAI(api_key=api_key, base_url=api_base)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a careful algorithm engineer. Return code only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=3072,
    )
    raw_text = response.choices[0].message.content or ""
    candidate_code = _extract_python_code(raw_text)

    raw_path = output_dir / "raw_response.txt"
    candidate_path = output_dir / "candidate_program.py"
    raw_path.write_text(raw_text, encoding="utf-8")
    candidate_path.write_text(candidate_code, encoding="utf-8")

    evaluate = _load_evaluator(evaluator_path)
    metrics = evaluate(str(candidate_path))
    summary = {
        "status": "completed",
        "provider": args.provider,
        "model": model,
        "api_base_host": api_base.split("//")[-1].split("/")[0],
        "initial_program": str(initial_path),
        "evaluator": str(evaluator_path),
        "candidate_program": str(candidate_path),
        "signature": args.signature,
        "metrics": {k: _jsonable(v) for k, v in dict(metrics).items()},
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

