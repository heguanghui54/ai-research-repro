from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .llm import chat_json
from .prompts import REVIEW_SYSTEM


def fallback_review(report: str, metrics: dict[str, Any]) -> dict[str, Any]:
    score = 6.0
    if metrics.get("delta_val_loss", 0) < 0:
        score += 1.0
    return {
        "overall": score,
        "strengths": ["Clear end-to-end workflow", "Reproducible local benchmark"],
        "weaknesses": ["Small benchmark", "Limited novelty if ideas are only hyperparameter edits"],
        "recommendation": "revise",
    }


def review_report(
    report_text: str,
    *,
    metrics: dict[str, Any],
    model: str = "gpt-4o-mini",
) -> dict[str, Any]:
    user = f"""Review the following report and metrics.

METRICS:
{json.dumps(metrics, indent=2)}

REPORT:
{report_text}
"""
    result = chat_json(system=REVIEW_SYSTEM, user=user, model=model, fallback=lambda: fallback_review(report_text, metrics))
    if isinstance(result, dict):
        result.setdefault("overall", 0.0)
        result.setdefault("strengths", [])
        result.setdefault("weaknesses", [])
        result.setdefault("recommendation", "revise")
        return result
    return fallback_review(report_text, metrics)


def save_review(review: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review, indent=2), encoding="utf-8")

