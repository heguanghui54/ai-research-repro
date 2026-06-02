#!/usr/bin/env python3
"""Audit executed delayed-value replay case artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
DEFAULT_RUN_DIR = DOC_DIR / "experiments" / "delayed_value_replay_case_paper_105_review_1_20260602_235500"
CONDITIONS = [
    "paper_only",
    "raw_review_guided",
    "six_gate_hybrid_guided",
    "shuffled_review_control",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_ok(path: Path, min_bytes: int = 20) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def _strict_label(scores: dict[str, Any]) -> tuple[str, list[str]]:
    per = scores.get("per_condition", {})
    reasons: list[str] = []
    missing = [condition for condition in CONDITIONS if condition not in per]
    if missing:
        return "invalid", [f"missing condition scores: {missing}"]
    paper = per["paper_only"]
    shuffled = per["shuffled_review_control"]
    positives = []
    for condition in ["raw_review_guided", "six_gate_hybrid_guided"]:
        row = per[condition]
        short_ok = row.get("short_term_score", 0) < paper.get("short_term_score", 0)
        frontier_ok = row.get("frontier_alignment_score", 0) > paper.get("frontier_alignment_score", 0)
        control_ok = row.get("frontier_alignment_score", 0) > shuffled.get("frontier_alignment_score", 0)
        action_ok = row.get("actionability_score", 0) >= 4
        specific_ok = row.get("specificity_score", 0) >= 4
        reasons.append(
            f"{condition}: short_ok={short_ok}, frontier_ok={frontier_ok}, "
            f"control_ok={control_ok}, action_ok={action_ok}, specific_ok={specific_ok}"
        )
        if short_ok and frontier_ok and control_ok and action_ok and specific_ok:
            positives.append(condition)
    return ("positive" if positives else "mixed_or_inconclusive"), reasons


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []
    summary_path = run_dir / "summary.json"
    scores_path = run_dir / "condition_scores.json"
    readme_path = run_dir / "README.md"
    for path in [summary_path, scores_path, readme_path]:
        if not _file_ok(path):
            errors.append(f"missing required replay artifact: {_rel(path)}")
    for condition in CONDITIONS:
        for suffix in ["_artifact.md"]:
            path = run_dir / f"{condition}{suffix}"
            if not _file_ok(path, min_bytes=100):
                errors.append(f"missing condition artifact: {_rel(path)}")
    for name in ["generation_prompt.txt", "generation_raw_response.txt", "scoring_prompt.txt", "scoring_raw_response.txt"]:
        if not _file_ok(run_dir / name, min_bytes=100):
            errors.append(f"missing prompt/response artifact: {_rel(run_dir / name)}")

    summary = _load_json(summary_path) if summary_path.exists() else {}
    scores = _load_json(scores_path) if scores_path.exists() else {}
    strict_label, strict_reasons = _strict_label(scores)
    reported_label = (summary.get("scoring") or {}).get("delayed_value_label")
    model_label = (summary.get("scoring") or {}).get("model_delayed_value_label")

    if summary.get("status") != "executed_delayed_value_replay_case":
        errors.append("summary status is not executed_delayed_value_replay_case")
    if summary.get("live_model_calls") != 2:
        errors.append("summary does not report 2 live model calls")
    if reported_label != strict_label:
        errors.append(f"reported delayed-value label {reported_label} does not match strict label {strict_label}")
    if model_label == "positive" and strict_label != "positive":
        warnings.append("raw model judge labeled the case positive, but strict preregistered rule does not")
    if "does not rerun" not in summary.get("claim_boundary", "") or "benchmarks" not in summary.get("claim_boundary", ""):
        errors.append("summary missing benchmark non-execution boundary")

    safe_case = str(summary.get("case_id") or run_dir.name).replace("/", "_")
    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "run_dir": _rel(run_dir),
        "case_id": summary.get("case_id"),
        "live_model_calls": summary.get("live_model_calls"),
        "generation_model": summary.get("generation_model"),
        "judge_model": summary.get("judge_model"),
        "model_delayed_value_label": model_label,
        "strict_delayed_value_label": strict_label,
        "reported_delayed_value_label": reported_label,
        "winner_short_term": scores.get("winner_short_term"),
        "winner_frontier": scores.get("winner_frontier"),
        "strict_rule_reasons": strict_reasons,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "A pass means one live four-condition replay case was generated and scored, "
            "with the delayed-value label checked against the preregistered rule. It "
            "does not mean benchmark experiments or human expert ratings were run."
        ),
    }
    suffix = "" if run_dir == DEFAULT_RUN_DIR else f"_{safe_case}"
    json_path = AUDIT_DIR / f"delayed_value_replay_case_audit{suffix}.json"
    md_path = AUDIT_DIR / f"delayed_value_replay_case_audit{suffix}.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Delayed-Value Replay Case Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Run dir: `{audit['run_dir']}`",
        f"- Case ID: `{audit['case_id']}`",
        f"- Live model calls: `{audit['live_model_calls']}`",
        f"- Model delayed-value label: `{audit['model_delayed_value_label']}`",
        f"- Strict delayed-value label: `{audit['strict_delayed_value_label']}`",
        f"- Winner short-term: `{audit['winner_short_term']}`",
        f"- Winner frontier: `{audit['winner_frontier']}`",
        "",
        "## Strict Rule Checks",
        "",
    ]
    lines.extend(f"- {reason}" for reason in strict_reasons)
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
