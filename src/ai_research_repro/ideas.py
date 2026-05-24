from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from .llm import chat_json
from .prompts import IDEA_SYSTEM, IDEA_USER


@dataclass
class Idea:
    title: str
    hypothesis: str
    patch: dict[str, Any]
    expected_effect: str
    risk: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def baseline_summary(default_cfg: dict[str, Any]) -> str:
    return json.dumps(default_cfg, indent=2)


def fallback_ideas(num_ideas: int) -> list[dict[str, Any]]:
    proposals = [
        {
            "title": "Wider embedding with stronger regularization",
            "hypothesis": "A larger embedding and hidden layer should improve representation capacity.",
            "patch": {"n_embd": 48, "hidden_size": 192, "weight_decay": 0.0005, "lr": 0.04},
            "expected_effect": "Lower validation loss and slightly better sample quality.",
            "risk": "May require a bit more training to converge.",
        },
        {
            "title": "Longer context window",
            "hypothesis": "A longer context can help the model exploit more surrounding characters.",
            "patch": {"block_size": 48, "lr": 0.045},
            "expected_effect": "Improved validation loss if the extra context is useful.",
            "risk": "Each step becomes slightly more expensive.",
        },
        {
            "title": "Gentler optimization schedule",
            "hypothesis": "Lower learning rate and more steps should stabilize training.",
            "patch": {"lr": 0.035, "max_steps": 550, "grad_clip": 0.8},
            "expected_effect": "Smoother learning curve and potentially lower final loss.",
            "risk": "Longer runtime for one candidate.",
        },
        {
            "title": "Sharper compression through a smaller hidden layer",
            "hypothesis": "A narrower hidden layer may force more efficient reuse of features.",
            "patch": {"hidden_size": 96, "weight_decay": 0.0002, "lr": 0.05},
            "expected_effect": "Could improve generalization if the baseline overfits.",
            "risk": "May underfit if capacity becomes too small.",
        },
    ]
    return proposals[:num_ideas]


def generate_ideas(
    *,
    num_ideas: int,
    default_cfg: dict[str, Any],
    model: str = "gpt-4o-mini",
) -> list[dict[str, Any]]:
    user = IDEA_USER.format(baseline_summary=baseline_summary(default_cfg), num_ideas=num_ideas)

    def _fallback() -> list[dict[str, Any]]:
        return fallback_ideas(num_ideas)

    result = chat_json(system=IDEA_SYSTEM, user=user, model=model, fallback=_fallback)
    if isinstance(result, dict) and "ideas" in result:
        result = result["ideas"]
    if not isinstance(result, list):
        return fallback_ideas(num_ideas)
    cleaned: list[dict[str, Any]] = []
    for item in result[:num_ideas]:
        if not isinstance(item, dict):
            continue
        cleaned.append(
            {
                "title": str(item.get("title", "Untitled idea")),
                "hypothesis": str(item.get("hypothesis", "")),
                "patch": dict(item.get("patch", {})),
                "expected_effect": str(item.get("expected_effect", "")),
                "risk": str(item.get("risk", "")),
            }
        )
    return cleaned or fallback_ideas(num_ideas)


def novelty_filter(ideas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    filtered = []
    for idea in ideas:
        key = idea["title"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        filtered.append(idea)
    return filtered
