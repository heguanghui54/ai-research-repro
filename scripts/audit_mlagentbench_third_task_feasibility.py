#!/usr/bin/env python3
"""Audit the MLAgentBench third-task feasibility probe."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments" / "mlagentbench_third_task_feasibility_20260603"
AUDIT_DIR = DOC_DIR / "audits"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = EXP_DIR / "summary.json"
    summary = _load_json(summary_path)
    logs_dir = EXP_DIR / "logs"
    prepare_exit = _read(logs_dir / "babylm_prepare.exit").strip()
    train_exit = _read(logs_dir / "babylm_train_tiny.exit").strip()
    train_stderr = _read(logs_dir / "babylm_train_tiny.stderr.log")
    prepare_stdout = _read(logs_dir / "babylm_prepare.stdout.log")
    prepare_stderr = _read(logs_dir / "babylm_prepare.stderr.log")

    candidate = summary["candidate_inventory"]["candidate_probed"][0]
    blocked_tasks = summary["candidate_inventory"]["not_selected_due_to_access_or_cost"]
    blocked_types = {entry["blocker_type"] for entry in blocked_tasks}
    expected_blockers = {
        "kaggle_account_cli_or_competition_consent",
        "llm_api_or_external_scholarly_service_task",
        "gpu_and_model_access_cost",
        "huggingface_dataset_network",
        "cpu_runtime_or_checkpoint_cost",
    }

    checks = {
        "summary_marks_unscored": summary.get("status") == "setup_accessible_but_unscored",
        "babylm_prepare_succeeded": candidate.get("prepare_exit_code") == 0 and prepare_exit == "0",
        "babylm_download_logged": "babylm_data.zip" in prepare_stdout
        and "github.com/babylm" in prepare_stderr,
        "tiny_train_failed_as_blocker_not_score": candidate.get("tiny_train_exit_code") == 1
        and train_exit == "1",
        "hf_gpt2_blocker_logged": "Network is unreachable" in train_stderr
        and "gpt2" in train_stderr
        and "AutoTokenizer.from_pretrained" in train_stderr,
        "compatibility_repairs_recorded": len(candidate.get("compatibility_repairs", [])) >= 4,
        "all_expected_blocker_categories_present": expected_blockers.issubset(blocked_types),
        "claim_boundary_says_no_third_score": "does not add a third scored" in summary.get("claim_boundary", ""),
    }

    status = "pass" if all(checks.values()) else "fail"
    audit = {
        "status": status,
        "created_at": _utc_now(),
        "evidence_class": "mlagentbench_third_task_feasibility_inventory",
        "summary_path": _rel(summary_path),
        "checks": checks,
        "babylm": {
            "prepare_exit": prepare_exit,
            "tiny_train_exit": train_exit,
            "evidence_class": candidate.get("evidence_class"),
            "blocking_error": candidate.get("blocking_error"),
            "logs": [_rel(EXP_DIR / log_path) for log_path in candidate.get("logs", [])],
        },
        "blocked_task_categories": sorted(blocked_types),
        "claim_boundary": summary.get("claim_boundary"),
        "recommended_next_step": summary.get("recommended_next_step"),
    }

    json_path = AUDIT_DIR / "mlagentbench_third_task_feasibility_audit.json"
    md_path = AUDIT_DIR / "mlagentbench_third_task_feasibility_audit.md"
    json_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(
        "\n".join(
            [
                "# MLAgentBench Third-Task Feasibility Audit",
                "",
                f"Status: `{status}`",
                "",
                "## Checks",
                "",
                *[f"- `{name}`: {value}" for name, value in checks.items()],
                "",
                "## BabyLM Probe",
                "",
                f"- Prepare exit: `{prepare_exit}`",
                f"- Tiny train exit: `{train_exit}`",
                f"- Evidence class: `{candidate.get('evidence_class')}`",
                f"- Blocker: {candidate.get('blocking_error')}",
                "",
                "## Boundary",
                "",
                summary.get("claim_boundary", ""),
                "",
                "## Next Step",
                "",
                summary.get("recommended_next_step", ""),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for artifact_path in [_rel(json_path), _rel(md_path), _rel(summary_path)]:
        if isinstance(artifacts, list) and artifact_path not in artifacts:
            artifacts.append(artifact_path)
    manifest["mlagentbench_third_task_feasibility_audit"] = {
        "json": _rel(json_path),
        "markdown": _rel(md_path),
        "summary": _rel(summary_path),
        "status": status,
        "evidence_class": audit["evidence_class"],
    }
    next_required = manifest.setdefault("next_required_evidence", [])
    requirement = (
        "Cache GPT-2 tokenizer/config assets or otherwise repair BabyLM before "
        "counting it as a third scored official MLAgentBench task; until then, "
        "treat the third-task probe as setup/blocker evidence only."
    )
    if requirement not in next_required:
        next_required.append(requirement)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
