#!/usr/bin/env python3
"""Aggregate executed live Temporal Frontier Replay cases."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"

CASE_RUNS = [
    EXP_DIR / "delayed_value_replay_case_paper_105_review_1_20260602_235500",
    EXP_DIR / "delayed_value_replay_case_paper_132_review_2_20260603_002500",
]

CROSS_MODEL_RUNS = [
    EXP_DIR / "delayed_value_replay_cross_model_judge_20260603_001500",
    EXP_DIR / "delayed_value_replay_cross_model_judge_paper_132_review_2_20260603_003000",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> str:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _case_row(run_dir: Path) -> dict[str, Any]:
    summary = _load_json(run_dir / "summary.json")
    scoring = summary.get("scoring", {})
    return {
        "case_id": summary.get("case_id"),
        "title": summary.get("title"),
        "run_dir": _rel(run_dir),
        "status": summary.get("status"),
        "judge_model": summary.get("judge_model"),
        "model_label": scoring.get("model_delayed_value_label"),
        "strict_label": scoring.get("delayed_value_label"),
        "winner_short_term": scoring.get("winner_short_term"),
        "winner_frontier": scoring.get("winner_frontier"),
        "best_review_signal": scoring.get("best_review_signal"),
        "failure_modes": scoring.get("failure_modes_observed", []),
        "strict_note": scoring.get("deterministic_label_note"),
    }


def _cross_row(run_dir: Path) -> dict[str, Any]:
    summary = _load_json(run_dir / "summary.json")
    return {
        "run_dir": _rel(run_dir),
        "source_case_run": summary.get("source_case_run"),
        "models_attempted": summary.get("models_attempted", []),
        "models_succeeded": summary.get("models_succeeded", []),
        "errors": summary.get("errors", {}),
        "aggregate": summary.get("aggregate", {}),
        "judgement_digest": {
            model: {
                "model_label": judgement.get("model_delayed_value_label"),
                "strict_label": judgement.get("strict_delayed_value_label"),
                "winner_short_term": judgement.get("winner_short_term"),
                "winner_frontier": judgement.get("winner_frontier"),
                "failure_modes_observed": judgement.get("failure_modes_observed", [])[:4],
            }
            for model, judgement in summary.get("judgements", {}).items()
        },
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Live TFR Replay Aggregate Summary",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Executed case count: `{summary['executed_case_count']}`",
        f"- Same-model raw positive labels: `{summary['same_model_raw_positive_count']}`",
        f"- Strict positive labels: `{summary['strict_positive_count']}`",
        f"- Cross-model successful judges: `{summary['cross_model_successful_judge_count']}`",
        f"- Cross-model strict positive labels: `{summary['cross_model_strict_positive_count']}`",
        "",
        "## Same-Model Case Results",
        "",
        "| Case | Model label | Strict label | Short-term winner | Frontier winner |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in summary["case_rows"]:
        lines.append(
            f"| `{row['case_id']}` | `{row['model_label']}` | `{row['strict_label']}` | "
            f"`{row['winner_short_term']}` | `{row['winner_frontier']}` |"
        )
    lines.extend(["", "## Cross-Model Results", ""])
    for row in summary["cross_model_rows"]:
        lines.append(f"- Source `{row['source_case_run']}`")
        for model, digest in row["judgement_digest"].items():
            lines.append(
                f"  - `{model}`: strict `{digest['strict_label']}`, model `{digest['model_label']}`, "
                f"frontier winner `{digest['winner_frontier']}`"
            )
        if row["errors"]:
            lines.append(f"  - archived errors: `{row['errors']}`")
    lines.extend(["", "## Interpretation", "", summary["interpretation"], ""])
    lines.extend(["## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["live_tfr_replay_aggregate"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "executed_case_count": summary["executed_case_count"],
        "strict_positive_count": summary["strict_positive_count"],
        "cross_model_strict_positive_count": summary["cross_model_strict_positive_count"],
        "claim_boundary": summary["claim_boundary"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    run_id = "live_tfr_replay_aggregate_20260603_003500"
    out_dir = EXP_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    case_rows = [_case_row(path) for path in CASE_RUNS]
    cross_rows = [_cross_row(path) for path in CROSS_MODEL_RUNS]

    same_model_raw_positive_count = sum(row["model_label"] == "positive" for row in case_rows)
    strict_positive_count = sum(row["strict_label"] == "positive" for row in case_rows)
    cross_success = sum(len(row["models_succeeded"]) for row in cross_rows)
    cross_strict_positive = sum(
        counts.get("positive", 0)
        for row in cross_rows
        for counts in [row["aggregate"].get("strict_label_counts", {})]
    )
    summary: dict[str, Any] = {
        "run_id": run_id,
        "timestamp_utc": _utc_now(),
        "status": "live_tfr_replay_aggregate",
        "executed_case_count": len(case_rows),
        "same_model_raw_positive_count": same_model_raw_positive_count,
        "strict_positive_count": strict_positive_count,
        "cross_model_successful_judge_count": cross_success,
        "cross_model_strict_positive_count": cross_strict_positive,
        "case_rows": case_rows,
        "cross_model_rows": cross_rows,
        "interpretation": (
            "Across two live four-condition TFR cases, the same-model GPT judge "
            "labels both cases positive before deterministic rule repair, but the "
            "strict preregistered delayed-value rule finds zero positive cases. "
            "Claude cross-model review also finds zero strict positive cases while "
            "often selecting the six-gate artifact as the frontier winner. This "
            "supports TFR as a model-optimism guard and failure-mode diagnostic, not "
            "as evidence that delayed-value review signals have already been found."
        ),
        "claim_boundary": (
            "This aggregate summarizes model-generated mini-paper replay artifacts "
            "and model judges. It does not include benchmark reruns, human expert "
            "ratings, or proof that human reviews improve long-horizon scientific outcomes."
        ),
    }
    summary_path = out_dir / "summary.json"
    summary["summary_path"] = _rel(summary_path)
    paths = [
        _write(summary_path, json.dumps(summary, ensure_ascii=False, indent=2)),
        _write(out_dir / "README.md", _markdown(summary)),
        "scripts/build_live_tfr_replay_summary.py",
    ]
    _update_manifest(paths, summary)
    print(json.dumps({"summary": _rel(summary_path), "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
