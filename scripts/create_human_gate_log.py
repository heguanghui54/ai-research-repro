#!/usr/bin/env python3
"""Create and validate a Co-Pilot AI Scientist v3 human-gate log."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
TEMPLATE_PATH = ROOT / "skills" / "co-pilot-ai-scientist-v3" / "templates" / "human_gate_log_template.json"
SCHEMA_PATH = DOC_DIR / "human_gate_schema.json"
RUBRIC_PATH = DOC_DIR / "taste_insight_rubric.json"


REQUIRED_ATTENTION_FIELDS = [
    "active_review_minutes",
    "wall_clock_latency_minutes",
    "options_reviewed",
    "artifacts_reviewed_count",
    "decision_count",
]

REQUIRED_TASTE_FIELDS = [
    "rubric_version",
    "scores",
    "taste_insight_score",
    "qualitative_rationale",
    "non_metric_factors",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_timestamp(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _minutes_between(start: str, end: str) -> float:
    delta = _parse_timestamp(end) - _parse_timestamp(start)
    return round(delta.total_seconds() / 60, 6)


def _parse_option(value: str) -> dict[str, Any]:
    parts = value.split("::", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise argparse.ArgumentTypeError("options must be formatted as option_id::summary")
    return {"option_id": parts[0], "summary": parts[1], "score": None, "evidence": [], "risks": []}


def _parse_taste_score(value: str) -> tuple[str, float]:
    parts = value.split("=", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise argparse.ArgumentTypeError("taste scores must be formatted as dimension=value")
    try:
        score = float(parts[1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("taste score value must be numeric") from exc
    return parts[0], score


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _load_rubric_dimensions(rubric: dict[str, Any]) -> list[str]:
    return [
        item["name"]
        for item in rubric.get("dimensions", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    ]


def _valid_taste_score(value: Any) -> bool:
    return _is_number(value) and 1 <= float(value) <= 5


def _validate(
    schema: dict[str, Any],
    gate: dict[str, Any],
    *,
    require_complete_attention: bool,
    require_complete_taste: bool,
    rubric_dimensions: list[str],
) -> list[str]:
    errors: list[str] = []
    for field in schema.get("required", []):
        if field not in gate:
            errors.append(f"missing required field: {field}")
    gate_types = schema.get("properties", {}).get("gate_type", {}).get("enum", [])
    if gate.get("gate_type") not in gate_types:
        errors.append(f"invalid gate_type: {gate.get('gate_type')}")
    if not gate.get("options"):
        errors.append("options must contain at least one option")
    cost = gate.get("attention_cost")
    if require_complete_attention:
        if not isinstance(cost, dict):
            errors.append("attention_cost must be an object")
        else:
            for field in REQUIRED_ATTENTION_FIELDS:
                value = cost.get(field)
                if not _is_number(value):
                    errors.append(f"incomplete attention_cost.{field}")
    taste = gate.get("taste_insight")
    if require_complete_taste:
        if not isinstance(taste, dict):
            errors.append("taste_insight must be an object")
        else:
            for field in REQUIRED_TASTE_FIELDS:
                if field not in taste:
                    errors.append(f"incomplete taste_insight.{field}")
            score_map = taste.get("scores")
            if not isinstance(score_map, dict):
                errors.append("taste_insight.scores must be an object")
            else:
                for dimension in rubric_dimensions:
                    if not _valid_taste_score(score_map.get(dimension)):
                        errors.append(f"incomplete taste_insight.scores.{dimension}")
            if not _valid_taste_score(taste.get("taste_insight_score")):
                errors.append("incomplete taste_insight.taste_insight_score")
            rationale = taste.get("qualitative_rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                errors.append("incomplete taste_insight.qualitative_rationale")
            factors = taste.get("non_metric_factors")
            if (
                not isinstance(factors, list)
                or not factors
                or not all(isinstance(item, str) and item.strip() for item in factors)
            ):
                errors.append("incomplete taste_insight.non_metric_factors")
    return errors


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# {summary['audit_title']}",
        "",
        f"Audit date: {summary['audit_date']}",
        "",
        summary["interpretation"],
        "",
        "## Result",
        "",
        f"- Overall status: {summary['overall_status']}",
        f"- Generated gate log: `{summary['generated_gate_log']}`",
        f"- Complete attention-cost record: {summary['complete_attention_cost']}",
        f"- Complete taste/insight record: {summary['complete_taste_insight']}",
        f"- Validation errors: {len(summary['validation_errors'])}",
        "",
        "## Attention Cost",
        "",
    ]
    for key, value in summary["attention_cost"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Taste/Insight", ""])
    if summary.get("taste_insight"):
        for key, value in summary["taste_insight"].items():
            lines.append(f"- `{key}`: {value}")
    else:
        lines.append("- Not recorded.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            summary["follow_up_interpretation"],
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-id", required=True)
    parser.add_argument("--gate-type", required=True)
    parser.add_argument("--research-task-id", required=True)
    parser.add_argument("--option", action="append", type=_parse_option, required=True)
    parser.add_argument("--human-decision", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--affected-artifact", action="append", default=[])
    parser.add_argument("--downstream-budget-json", default="{}")
    parser.add_argument("--human-actor", default="human_scientist")
    parser.add_argument("--interaction-mode", default="async_review")
    parser.add_argument("--prompted-at-utc", required=True)
    parser.add_argument("--decision-at-utc", required=True)
    parser.add_argument("--active-review-minutes", type=float, required=True)
    parser.add_argument("--options-reviewed", type=int)
    parser.add_argument("--artifacts-reviewed-count", type=int, required=True)
    parser.add_argument("--decision-count", type=int, default=1)
    parser.add_argument("--notes", default="")
    parser.add_argument("--follow-up-check", action="append", default=[])
    parser.add_argument("--audit-title", default="Human Gate Logging Smoke Audit")
    parser.add_argument(
        "--interpretation",
        default=(
            "This smoke test verifies that future human gates can be logged with "
            "complete measurable attention-cost fields. The generated gate is synthetic "
            "tooling evidence and is not counted as a real experiment-performance gate."
        ),
    )
    parser.add_argument(
        "--follow-up-interpretation",
        default=(
            "The current archived human-gate logs still lack measured attention cost, "
            "but the package now includes a runnable path for prospective gates to "
            "record active review minutes, wall-clock latency, options reviewed, "
            "artifacts reviewed, decision count, and optional scientific "
            "taste/insight fields required by prospective matched-budget runs."
        ),
    )
    parser.add_argument("--taste-score", action="append", type=_parse_taste_score, default=[])
    parser.add_argument("--taste-insight-score", type=float)
    parser.add_argument("--taste-rationale")
    parser.add_argument("--non-metric-factor", action="append", default=[])
    parser.add_argument("--require-complete-attention", action="store_true")
    parser.add_argument("--require-complete-taste", action="store_true")
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit-json")
    parser.add_argument("--audit-md")
    args = parser.parse_args()

    template = _load_json(TEMPLATE_PATH)
    schema = _load_json(SCHEMA_PATH)
    rubric = _load_json(RUBRIC_PATH)
    rubric_dimensions = _load_rubric_dimensions(rubric)
    downstream_budget = json.loads(args.downstream_budget_json)
    wall_clock = _minutes_between(args.prompted_at_utc, args.decision_at_utc)
    taste_scores = dict(args.taste_score)

    gate = dict(template)
    gate.update(
        {
            "gate_id": args.gate_id,
            "gate_type": args.gate_type,
            "timestamp_utc": args.decision_at_utc,
            "research_task_id": args.research_task_id,
            "options": args.option,
            "human_decision": args.human_decision,
            "rationale": args.rationale,
            "affected_artifacts": args.affected_artifact,
            "downstream_budget": downstream_budget,
            "attention_cost": {
                "human_actor": args.human_actor,
                "interaction_mode": args.interaction_mode,
                "prompted_at_utc": args.prompted_at_utc,
                "decision_at_utc": args.decision_at_utc,
                "active_review_minutes": args.active_review_minutes,
                "wall_clock_latency_minutes": wall_clock,
                "options_reviewed": args.options_reviewed if args.options_reviewed is not None else len(args.option),
                "artifacts_reviewed_count": args.artifacts_reviewed_count,
                "decision_count": args.decision_count,
                "notes": args.notes,
            },
            "follow_up_checks": args.follow_up_check,
        }
    )
    if args.taste_score or args.taste_insight_score is not None or args.taste_rationale or args.non_metric_factor:
        gate["taste_insight"] = {
            "rubric_version": rubric.get("rubric_version"),
            "scores": {dimension: taste_scores.get(dimension) for dimension in rubric_dimensions},
            "taste_insight_score": args.taste_insight_score,
            "qualitative_rationale": args.taste_rationale or "",
            "non_metric_factors": args.non_metric_factor,
        }

    validation_errors = _validate(
        schema,
        gate,
        require_complete_attention=args.require_complete_attention,
        require_complete_taste=args.require_complete_taste,
        rubric_dimensions=rubric_dimensions,
    )
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "audit_date": args.decision_at_utc,
        "overall_status": "pass" if not validation_errors else "fail",
        "generated_gate_log": str(output.relative_to(ROOT)),
        "complete_attention_cost": not any(
            error.startswith("incomplete attention_cost") or error == "attention_cost must be an object"
            for error in validation_errors
        ),
        "complete_taste_insight": bool(gate.get("taste_insight")) and not any(
            error.startswith("incomplete taste_insight") or error == "taste_insight must be an object"
            for error in validation_errors
        ),
        "validation_errors": validation_errors,
        "attention_cost": gate["attention_cost"],
        "taste_insight": gate.get("taste_insight"),
        "audit_title": args.audit_title,
        "interpretation": args.interpretation,
        "follow_up_interpretation": args.follow_up_interpretation,
    }
    if args.audit_json:
        audit_json = ROOT / args.audit_json
        audit_json.parent.mkdir(parents=True, exist_ok=True)
        audit_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.audit_md:
        audit_md = ROOT / args.audit_md
        audit_md.parent.mkdir(parents=True, exist_ok=True)
        audit_md.write_text(_markdown(summary), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if validation_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
