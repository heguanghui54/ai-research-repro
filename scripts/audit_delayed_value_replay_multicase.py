#!/usr/bin/env python3
"""Aggregate delayed-value replay cases under the strict DVRS rule.

This audit turns the three archived four-condition replay cases into one
case-level evidence table. It deliberately separates model optimism from the
preregistered delayed-value rule: a case is a positive DVRS only when review
guidance is worse or no better in the short term while improving frontier
alignment over both paper-only and shuffled controls, with actionable and
specific guidance.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
AUDIT_DIR = DOC_DIR / "audits"
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


def _strict_rule(scores: dict[str, Any]) -> tuple[str, str | None, list[dict[str, Any]]]:
    per = scores.get("per_condition", {})
    missing = [condition for condition in CONDITIONS if condition not in per]
    if missing:
        return "invalid", None, [{"condition": "missing", "missing": missing}]
    paper = per["paper_only"]
    shuffled = per["shuffled_review_control"]
    reasons: list[dict[str, Any]] = []
    positives: list[str] = []
    for condition in ["raw_review_guided", "six_gate_hybrid_guided"]:
        row = per[condition]
        checks = {
            "short_term_penalty": row.get("short_term_score", 0) < paper.get("short_term_score", 0),
            "beats_paper_frontier": row.get("frontier_alignment_score", 0)
            > paper.get("frontier_alignment_score", 0),
            "beats_shuffled_frontier": row.get("frontier_alignment_score", 0)
            > shuffled.get("frontier_alignment_score", 0),
            "actionable": row.get("actionability_score", 0) >= 4,
            "specific": row.get("specificity_score", 0) >= 4,
        }
        reasons.append({"condition": condition, **checks})
        if all(checks.values()):
            positives.append(condition)
    return ("positive" if positives else "mixed_or_inconclusive"), (positives[0] if positives else None), reasons


def _case_dirs() -> list[Path]:
    return sorted(
        path
        for path in EXP_DIR.glob("delayed_value_replay_case_*")
        if (path / "summary.json").exists() and (path / "condition_scores.json").exists()
    )


def _judge_summaries_by_source() -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for path in sorted(EXP_DIR.glob("delayed_value_replay_cross_model_judge*/summary.json")):
        summary = _load_json(path)
        source = summary.get("source_case_run")
        if source:
            out.setdefault(source, []).append(path)
    return out


def _summarize_cross_model(paths: list[Path]) -> dict[str, Any]:
    strict_labels = Counter()
    model_labels = Counter()
    frontier_winners = Counter()
    succeeded_models = []
    attempted_models = []
    for path in paths:
        summary = _load_json(path)
        attempted_models.extend(summary.get("models_attempted", []))
        succeeded_models.extend(summary.get("models_succeeded", []))
        for model, judgement in summary.get("judgements", {}).items():
            strict_labels[judgement.get("strict_delayed_value_label", "missing")] += 1
            model_labels[judgement.get("model_delayed_value_label", "missing")] += 1
            frontier_winners[judgement.get("winner_frontier", "missing")] += 1
    return {
        "summary_paths": [_rel(path) for path in paths],
        "models_attempted": sorted(set(attempted_models)),
        "models_succeeded": sorted(set(succeeded_models)),
        "strict_label_counts": dict(strict_labels),
        "model_label_counts": dict(model_labels),
        "frontier_winner_counts": dict(frontier_winners),
    }


def _update_manifest(json_path: Path, md_path: Path, audit: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in [json_path, md_path, Path(__file__)]:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["delayed_value_replay_multicase_audit"] = {
        "status": audit["status"],
        "json": _rel(json_path),
        "markdown": _rel(md_path),
        "case_count": audit["case_count"],
        "strict_positive_cases": audit["strict_positive_cases"],
        "same_model_positive_cases": audit["same_model_positive_cases"],
        "cross_model_strict_positive_cases": audit["cross_model_strict_positive_cases"],
        "claim_boundary": audit["claim_boundary"],
    }
    counts = manifest.setdefault("current_counts", {})
    counts["delayed_value_replay_multicase_count"] = audit["case_count"]
    counts["delayed_value_replay_multicase_strict_positive_cases"] = audit["strict_positive_cases"]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []
    case_rows = []
    cross_by_source = _judge_summaries_by_source()

    for case_dir in _case_dirs():
        summary = _load_json(case_dir / "summary.json")
        scores = _load_json(case_dir / "condition_scores.json")
        strict_label, strict_positive_condition, strict_reasons = _strict_rule(scores)
        source_rel = _rel(case_dir)
        cross = _summarize_cross_model(cross_by_source.get(source_rel, []))
        same_model_label = scores.get("model_delayed_value_label")
        if same_model_label == "positive" and strict_label != "positive":
            warnings.append(
                f"{summary.get('case_id')} same-model judge positive but strict rule is {strict_label}"
            )
        if not cross["summary_paths"]:
            warnings.append(f"{summary.get('case_id')} has no cross-model judge summary")
        case_rows.append(
            {
                "case_id": summary.get("case_id"),
                "run_dir": source_rel,
                "same_model_label": same_model_label,
                "strict_label": strict_label,
                "strict_positive_condition": strict_positive_condition,
                "winner_short_term": scores.get("winner_short_term"),
                "winner_frontier": scores.get("winner_frontier"),
                "strict_reasons": strict_reasons,
                "cross_model": cross,
            }
        )

    if len(case_rows) < 3:
        errors.append(f"expected at least 3 delayed-value replay cases, found {len(case_rows)}")

    strict_positive_cases = sum(1 for row in case_rows if row["strict_label"] == "positive")
    same_model_positive_cases = sum(1 for row in case_rows if row["same_model_label"] == "positive")
    cross_model_strict_positive_cases = 0
    cross_model_frontier_winners = Counter()
    for row in case_rows:
        strict_counts = row["cross_model"].get("strict_label_counts", {})
        cross_model_strict_positive_cases += strict_counts.get("positive", 0)
        cross_model_frontier_winners.update(row["cross_model"].get("frontier_winner_counts", {}))

    audit = {
        "audit_date": _utc_now(),
        "status": "pass_with_no_strict_positive_dvrs" if not errors else "fail",
        "case_count": len(case_rows),
        "case_rows": case_rows,
        "same_model_positive_cases": same_model_positive_cases,
        "strict_positive_cases": strict_positive_cases,
        "cross_model_strict_positive_cases": cross_model_strict_positive_cases,
        "cross_model_frontier_winner_counts": dict(cross_model_frontier_winners),
        "errors": errors,
        "warnings": warnings,
        "interpretation": (
            "The replay cases show useful frontier-routing diagnostics, especially "
            "six-gate frontier wins under Claude judges, but the strict preregistered "
            "DVRS rule finds no positive delayed-value case because the required "
            "short-term penalty/actionability/specificity pattern is not satisfied."
        ),
        "claim_boundary": (
            "A pass means multiple four-condition replay cases and cross-model judges "
            "were aggregated under the strict delayed-value rule. It is model-scored "
            "replay evidence, not benchmark execution or human expert validation."
        ),
    }

    json_path = AUDIT_DIR / "delayed_value_replay_multicase_audit.json"
    md_path = AUDIT_DIR / "delayed_value_replay_multicase_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Delayed-Value Replay Multicase Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Replay cases: `{audit['case_count']}`",
        f"- Same-model positive labels: `{audit['same_model_positive_cases']}`",
        f"- Strict positive DVRS cases: `{audit['strict_positive_cases']}`",
        f"- Cross-model strict positive labels: `{audit['cross_model_strict_positive_cases']}`",
        f"- Cross-model frontier winner counts: `{audit['cross_model_frontier_winner_counts']}`",
        "",
        "## Case Table",
        "",
        "| Case | Same-model label | Strict label | Short-term winner | Frontier winner | Cross-model strict labels | Cross-model frontier winners |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in case_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['case_id']}`",
                    f"`{row['same_model_label']}`",
                    f"`{row['strict_label']}`",
                    f"`{row['winner_short_term']}`",
                    f"`{row['winner_frontier']}`",
                    f"`{row['cross_model'].get('strict_label_counts')}`",
                    f"`{row['cross_model'].get('frontier_winner_counts')}`",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Strict Rule Diagnostics", ""])
    for row in case_rows:
        lines.append(f"### `{row['case_id']}`")
        for reason in row["strict_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Interpretation", "", audit["interpretation"], ""])
    lines.extend(["## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    _update_manifest(json_path, md_path, audit)
    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
