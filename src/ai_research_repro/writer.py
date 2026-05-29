from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .llm import chat_text
from .prompts import WRITE_SYSTEM


def fallback_report(idea: dict[str, Any], baseline: dict[str, Any], candidate: dict[str, Any]) -> str:
    delta = candidate["metrics"]["final_val_loss"] - baseline["metrics"]["final_val_loss"]
    return f"""# AI Research Reproduction Report

## Idea

**Title:** {idea["title"]}

**Hypothesis:** {idea["hypothesis"]}

**Patch:** `{json.dumps(idea["patch"])}`.

## Results

- Baseline validation loss: {baseline["metrics"]["final_val_loss"]:.4f}
- Candidate validation loss: {candidate["metrics"]["final_val_loss"]:.4f}
- Delta: {delta:.4f}

## Interpretation

The candidate {'improved' if delta < 0 else 'did not improve'} the baseline.

## Limitations

- The benchmark is intentionally small.
- The current version explores one idea at a time.
- Better scientific novelty screening is a future step.
"""


def write_report(
    idea: dict[str, Any],
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    model: str | None = None,
    provider: str | None = None,
) -> str:
    prompt = f"""Write a concise scientific report in markdown.
Use the following experiment data.

IDEA:
{json.dumps(idea, indent=2)}

BASELINE METRICS:
{json.dumps(baseline["metrics"], indent=2)}

CANDIDATE METRICS:
{json.dumps(candidate["metrics"], indent=2)}

HISTORY:
{json.dumps(candidate["history"], indent=2)}
"""
    result = chat_text(
        system=WRITE_SYSTEM,
        user=prompt,
        model=model,
        provider=provider,
        fallback=lambda: fallback_report(idea, baseline, candidate),
    )
    return result.text


def save_report(report: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
