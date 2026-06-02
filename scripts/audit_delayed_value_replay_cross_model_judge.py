#!/usr/bin/env python3
"""Audit cross-model delayed-value replay judging artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
AUDIT_DIR = DOC_DIR / "audits"
RUN_DIR = DOC_DIR / "experiments" / "delayed_value_replay_cross_model_judge_20260603_001500"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_ok(path: Path, min_bytes: int = 20) -> bool:
    return path.exists() and path.stat().st_size >= min_bytes


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []
    summary_path = RUN_DIR / "summary.json"
    if not _file_ok(summary_path):
        errors.append(f"missing summary: {_rel(summary_path)}")
        summary: dict[str, Any] = {}
    else:
        summary = _load_json(summary_path)

    for path in [RUN_DIR / "README.md", RUN_DIR / "judge_prompt.txt"]:
        if not _file_ok(path, min_bytes=100):
            errors.append(f"missing cross-model artifact: {_rel(path)}")

    judgements = summary.get("judgements", {})
    errors_by_model = summary.get("errors", {})
    aggregate = summary.get("aggregate", {})
    if summary.get("status") != "delayed_value_replay_cross_model_judge":
        errors.append("summary status is not delayed_value_replay_cross_model_judge")
    if not judgements:
        errors.append("no successful cross-model judgements")
    if aggregate.get("strict_label_counts", {}).get("positive", 0) > 0:
        warnings.append("at least one cross-model judge found strict positive delayed-value evidence")
    if aggregate.get("all_strict_positive"):
        errors.append("all_strict_positive should be false for current conservative evidence state")

    judgement_checks = []
    for model, judgement in judgements.items():
        raw_path = RUN_DIR / f"{model}_raw_response.txt"
        json_path = RUN_DIR / f"{model}_judgement.json"
        missing = []
        for path in [raw_path, json_path]:
            if not _file_ok(path, min_bytes=100):
                missing.append(_rel(path))
        if judgement.get("strict_delayed_value_label") not in {"positive", "mixed_or_inconclusive"}:
            errors.append(f"{model} has invalid strict label")
        if missing:
            errors.append(f"{model} missing judgement artifacts: {missing}")
        judgement_checks.append(
            {
                "model": model,
                "strict_label": judgement.get("strict_delayed_value_label"),
                "model_label": judgement.get("model_delayed_value_label"),
                "winner_frontier": judgement.get("winner_frontier"),
                "winner_short_term": judgement.get("winner_short_term"),
                "missing": missing,
            }
        )

    if errors_by_model:
        warnings.append(f"models with archived errors: {sorted(errors_by_model)}")

    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "run_dir": _rel(RUN_DIR),
        "models_attempted": summary.get("models_attempted", []),
        "models_succeeded": summary.get("models_succeeded", []),
        "models_failed": sorted(errors_by_model),
        "aggregate": aggregate,
        "judgement_checks": judgement_checks,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "A pass means at least one independent model judge scored the existing "
            "four-condition replay and the strict delayed-value label was archived. "
            "It is still model evaluation, not human expert review or benchmark execution."
        ),
    }
    json_path = AUDIT_DIR / "delayed_value_replay_cross_model_judge_audit.json"
    md_path = AUDIT_DIR / "delayed_value_replay_cross_model_judge_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Delayed-Value Replay Cross-Model Judge Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Run dir: `{audit['run_dir']}`",
        f"- Models attempted: `{', '.join(audit['models_attempted'])}`",
        f"- Models succeeded: `{', '.join(audit['models_succeeded'])}`",
        f"- Models failed: `{', '.join(audit['models_failed'])}`",
        f"- Strict label counts: `{aggregate.get('strict_label_counts')}`",
        f"- Frontier winner counts: `{aggregate.get('frontier_winner_counts')}`",
        "",
        "## Judgement Checks",
        "",
    ]
    for check in judgement_checks:
        lines.append(
            f"- `{check['model']}`: strict `{check['strict_label']}`, model `{check['model_label']}`, "
            f"frontier winner `{check['winner_frontier']}`, short-term winner `{check['winner_short_term']}`"
        )
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
