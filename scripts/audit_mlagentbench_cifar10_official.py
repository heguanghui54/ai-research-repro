#!/usr/bin/env python3
"""Audit the scored MLAgentBench CIFAR10/debug official benchmark run."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
AUDIT_DIR = DOC_DIR / "audits"
RUN_DIR = EXP_DIR / "mlagentbench_cifar10_debug_official_20260603"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _baseline_record(eval_payload: dict[str, Any]) -> dict[str, Any]:
    if len(eval_payload) != 1:
        raise ValueError(f"expected one MLAgentBench eval record, got {len(eval_payload)}")
    return next(iter(eval_payload.values()))


def _add_manifest_artifacts(paths: list[Path], payload: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    if not manifest_path.exists():
        return
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in [*paths, Path(__file__)]:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["mlagentbench_cifar10_official_audit"] = payload
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    baseline_eval_path = RUN_DIR / "baseline" / "eval.json"
    readme_path = RUN_DIR / "README.md"
    baseline_runner_log_path = RUN_DIR / "baseline" / "runner.stdout.log"
    baseline_eval_log_path = RUN_DIR / "baseline" / "eval.stdout.log"
    baseline_trace_path = RUN_DIR / "baseline" / "trace.json"
    baseline_time_path = RUN_DIR / "baseline" / "overall_time.txt"
    candidate_summary_path = RUN_DIR / "co_pilot_selected" / "summary.json"
    candidate_train_path = RUN_DIR / "co_pilot_selected" / "train.py"
    candidate_train_log_path = RUN_DIR / "co_pilot_selected" / "train.stdout.log"

    baseline_eval = _load_json(baseline_eval_path)
    baseline = _baseline_record(baseline_eval)
    candidate = _load_json(candidate_summary_path)

    baseline_score = baseline.get("final_score")
    candidate_score = candidate.get("official_eval_score")
    delta = candidate_score - baseline_score if isinstance(baseline_score, (int, float)) and isinstance(candidate_score, (int, float)) else None

    required_files = [
        readme_path,
        baseline_eval_path,
        baseline_runner_log_path,
        baseline_eval_log_path,
        baseline_trace_path,
        baseline_time_path,
        candidate_summary_path,
        candidate_train_path,
        candidate_train_log_path,
    ]
    file_checks = {path.name if path.parent.name == "baseline" else f"{path.parent.name}/{path.name}": path.exists() and path.stat().st_size > 0 for path in required_files}
    candidate_log_text = candidate_train_log_path.read_text(encoding="utf-8")

    checks = {
        "all_required_files_present": all(file_checks.values()),
        "baseline_official_eval_score_present": isinstance(baseline_score, (int, float)),
        "baseline_submitted_final_answer": baseline.get("submitted_final_answer") is True,
        "baseline_no_error_flags": baseline.get("extra", {}).get("error") is False
        and baseline.get("extra", {}).get("oom_error") is False
        and baseline.get("extra", {}).get("connection_error") is False,
        "candidate_official_eval_score_present": isinstance(candidate_score, (int, float)),
        "candidate_beats_baseline": delta is not None and delta > 0,
        "candidate_training_completed": "Done in" in candidate_log_text and "Epoch [8/8]" in candidate_log_text,
        "same_official_task": candidate.get("task") == "MLAgentBench debug / cifar10",
    }

    errors = [name for name, passed in checks.items() if not passed]
    audit = {
        "audit_date": _utc_now(),
        "status": "pass" if not errors else "fail",
        "head": _git_head(),
        "evidence_class": "scored_official_mlagentbench_non_fml_task",
        "task": "MLAgentBench debug / cifar10",
        "metric": "CIFAR10 test accuracy; higher is better",
        "baseline_eval_path": _rel(baseline_eval_path),
        "candidate_summary_path": _rel(candidate_summary_path),
        "baseline_score": baseline_score,
        "candidate_score": candidate_score,
        "delta": delta,
        "baseline_total_time_seconds": baseline.get("total_time"),
        "candidate_mode": candidate.get("mode"),
        "remote_baseline_run": "/home/heshi/work/copilotv3-mlagentbench-cifar10-debug-official-baseline-20260603",
        "remote_candidate_run": candidate.get("run_dir"),
        "file_checks": file_checks,
        "checks": checks,
        "errors": errors,
        "claim_boundary": (
            "This is a scored official MLAgentBench CIFAR10/debug task using the official "
            "evaluation script. It supports non-FML benchmark expansion and a concrete "
            "co-pilot-selected branch improvement over the starter baseline. It is still "
            "one task, one seed, and not independent human evidence or broad AI Scientist-v2 "
            "paper-quality superiority."
        ),
    }

    json_path = AUDIT_DIR / "mlagentbench_cifar10_official_audit.json"
    md_path = AUDIT_DIR / "mlagentbench_cifar10_official_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# MLAgentBench CIFAR10 Official Audit",
        "",
        f"- Audit date: `{audit['audit_date']}`",
        f"- Status: `{audit['status']}`",
        f"- Evidence class: `{audit['evidence_class']}`",
        f"- Task: `{audit['task']}`",
        f"- Metric: `{audit['metric']}`",
        f"- Baseline score: `{baseline_score}`",
        f"- Co-pilot selected score: `{candidate_score}`",
        f"- Delta: `{delta}`",
        f"- Baseline total time seconds: `{audit['baseline_total_time_seconds']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{name}`: `{passed}`" for name, passed in checks.items())
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    lines.extend(["", "## Claim Boundary", "", audit["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    _add_manifest_artifacts([*required_files, json_path, md_path], audit)
    print(json.dumps({"json": _rel(json_path), "markdown": _rel(md_path), "status": audit["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
