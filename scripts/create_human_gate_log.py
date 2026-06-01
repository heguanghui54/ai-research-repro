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


REQUIRED_ATTENTION_FIELDS = [
    "active_review_minutes",
    "wall_clock_latency_minutes",
    "options_reviewed",
    "artifacts_reviewed_count",
    "decision_count",
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


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate(schema: dict[str, Any], gate: dict[str, Any], *, require_complete_attention: bool) -> list[str]:
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
    return errors


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Human Gate Logging Smoke Audit",
        "",
        f"Audit date: {summary['audit_date']}",
        "",
        "This smoke test verifies that future human gates can be logged with",
        "complete measurable attention-cost fields. The generated gate is synthetic",
        "tooling evidence and is not counted as a real experiment-performance gate.",
        "",
        "## Result",
        "",
        f"- Overall status: {summary['overall_status']}",
        f"- Generated gate log: `{summary['generated_gate_log']}`",
        f"- Complete attention-cost record: {summary['complete_attention_cost']}",
        f"- Validation errors: {len(summary['validation_errors'])}",
        "",
        "## Attention Cost",
        "",
    ]
    for key, value in summary["attention_cost"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The current archived human-gate logs still lack measured attention cost,",
            "but the package now includes a runnable path for prospective gates to",
            "record active review minutes, wall-clock latency, options reviewed,",
            "artifacts reviewed, and decision count.",
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
    parser.add_argument("--require-complete-attention", action="store_true")
    parser.add_argument("--output", required=True)
    parser.add_argument("--audit-json")
    parser.add_argument("--audit-md")
    args = parser.parse_args()

    template = _load_json(TEMPLATE_PATH)
    schema = _load_json(SCHEMA_PATH)
    downstream_budget = json.loads(args.downstream_budget_json)
    wall_clock = _minutes_between(args.prompted_at_utc, args.decision_at_utc)

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

    validation_errors = _validate(schema, gate, require_complete_attention=args.require_complete_attention)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "audit_date": args.decision_at_utc,
        "overall_status": "pass" if not validation_errors else "fail",
        "generated_gate_log": str(output.relative_to(ROOT)),
        "complete_attention_cost": not validation_errors,
        "validation_errors": validation_errors,
        "attention_cost": gate["attention_cost"],
        "interpretation": "Synthetic tooling smoke; not counted as real human-gated experiment evidence.",
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
