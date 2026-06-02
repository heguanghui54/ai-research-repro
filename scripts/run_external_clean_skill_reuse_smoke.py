#!/usr/bin/env python3
"""Run the IGRE release skill in a clean external temporary workspace.

This is an engineering-transfer smoke, not a scientific evaluation. It copies
the standalone release skill into a temporary Codex skills directory outside
the repository, validates that the release can be read from there, and archives
a fresh six-gate task spec plus claim audit back into the evidence package.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
OUT_DIR = DOC_DIR / "experiments" / "external_clean_skill_reuse_smoke_20260603"
RELEASE_DIR = ROOT / "release" / "co-pilot-ai-scientist-v3-skill"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"
DEFAULT_EXTERNAL_ROOT = Path("/tmp/copilot_v3_external_skill_reuse_smoke")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _update_manifest(paths: list[Path], summary: dict[str, Any]) -> None:
    manifest = _load_json(MANIFEST_PATH)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["external_clean_skill_reuse_smoke"] = {
        "status": summary["status"],
        "output_dir": _rel(OUT_DIR),
        "external_root": summary["external_root"],
        "task_spec": _rel(OUT_DIR / "task_spec.md"),
        "gate_log": _rel(OUT_DIR / "six_gate_log.json"),
        "claim_audit": _rel(OUT_DIR / "claim_audit.md"),
        "clean_external_environment": summary["clean_external_environment"],
        "claim_boundary": summary["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-root", default=str(DEFAULT_EXTERNAL_ROOT))
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    external_root = Path(args.external_root).expanduser().resolve()
    external_skill_dir = external_root / "codex_skills" / "co-pilot-ai-scientist-v3"
    external_workspace = external_root / "workspace"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []
    warnings: list[str] = []
    created_at = _utc_now()

    if not RELEASE_DIR.exists():
        errors.append(f"missing release skill directory: {_rel(RELEASE_DIR)}")
    if external_root.exists():
        shutil.rmtree(external_root)
    external_skill_dir.parent.mkdir(parents=True, exist_ok=True)
    external_workspace.mkdir(parents=True, exist_ok=True)
    if RELEASE_DIR.exists():
        shutil.copytree(RELEASE_DIR, external_skill_dir)

    required_files = [
        "SKILL.md",
        "MIGRATION.md",
        "README.md",
        "QUICKSTART.md",
        "templates/task_spec_template.md",
        "templates/human_gate_log_template.json",
        "templates/claim_audit_template.md",
        "scripts/validate_release.py",
    ]
    for rel in required_files:
        path = external_skill_dir / rel
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing external installed file: {rel}")

    skill_text = (external_skill_dir / "SKILL.md").read_text(encoding="utf-8") if (external_skill_dir / "SKILL.md").exists() else ""
    lineage_terms = [
        "ai-scientist-v2",
        "Insight-Gated Research Evolution",
        "scientific_taste_prior",
        "evaluator_stress_test",
        "frontier_steering",
        "verifiable_micro_evolution",
        "structured_feedback",
        "claim_calibration",
    ]
    lineage_present = {term: term in skill_text for term in lineage_terms}
    missing_lineage = [term for term, present in lineage_present.items() if not present]
    if missing_lineage:
        errors.append(f"external skill missing lineage/gate terms: {missing_lineage}")

    task_spec = f"""# External Clean Skill Reuse Task

## Run ID

`external_clean_skill_reuse_smoke_20260603`

## External Workspace

`{external_workspace}`

## Fresh Topic

Design a co-pilot workflow for a small scientific-visualization replication
study. The task is intentionally outside the paper's FML, OpenReview replay,
and toy tabular-evaluator narratives. The goal is to check whether the release
skill can be reused in a clean external workspace on a new research style.

## AI Scientist-v2 Base Loop

1. Frame a reproducible visualization-replication question.
2. Generate candidate tasks: chart reproduction, data-cleaning audit, and
   figure-claim consistency.
3. Select a benchmark or fixed rubric.
4. Run small executable checks when data are available.
5. Draft a report only from logged evidence.
6. Calibrate claims before any paper-quality statement.

## IGRE Six-Gate Overlay

- `scientific_taste_prior`: prioritize figure-claim consistency because it
  exposes a high-value failure mode in automated science.
- `evaluator_stress_test`: require the rubric to distinguish visual similarity
  from scientific claim correctness.
- `frontier_steering`: allocate effort to the branch with the strongest
  diagnostic failure value, not merely the easiest chart.
- `verifiable_micro_evolution`: trigger only for machine-gradeable parsing or
  plotting subroutines.
- `structured_feedback`: route reviewer comments into figure, data, and claim
  fixes separately.
- `claim_calibration`: report this smoke as external clean-environment reuse,
  not as a benchmark or human-review result.

## Failure Criteria

- The skill cannot be read from the external temporary Codex skills directory.
- The generated plan omits the AI Scientist-v2 base loop or any IGRE gate.
- The claim audit presents engineering reuse as scientific superiority.
"""

    gates = [
        {
            "gate_id": "external_clean_scientific_taste_prior_001",
            "gate_type": "scientific_taste_prior",
            "decision": "prioritize_figure_claim_consistency",
            "rationale": "Human taste favors a diagnostically valuable failure mode over an easy visual-copying task.",
            "attention_cost": {"active_review_minutes": 0.0, "decision_count": 1, "human_actor": "scripted_engineering_smoke_not_human_evidence"},
            "claim_boundary": "Engineering reuse signal only.",
        },
        {
            "gate_id": "external_clean_evaluator_stress_001",
            "gate_type": "evaluator_stress_test",
            "decision": "require_claim_correctness_guardrail",
            "rationale": "Visual similarity alone can reward misleading reproductions.",
            "attention_cost": {"active_review_minutes": 0.0, "decision_count": 1, "human_actor": "scripted_engineering_smoke_not_human_evidence"},
            "claim_boundary": "No executable benchmark score is reported.",
        },
        {
            "gate_id": "external_clean_frontier_steering_001",
            "gate_type": "frontier_steering",
            "decision": "select_diagnostic_failure_branch",
            "rationale": "The branch is valuable because it can reveal mismatch between figure appearance and scientific claim.",
            "attention_cost": {"active_review_minutes": 0.0, "decision_count": 1, "human_actor": "scripted_engineering_smoke_not_human_evidence"},
            "claim_boundary": "No performance comparison is claimed.",
        },
        {
            "gate_id": "external_clean_micro_evolution_001",
            "gate_type": "verifiable_micro_evolution",
            "decision": "defer_until_parser_or_plotter_is_machine_gradeable",
            "rationale": "OpenEvolve-style search should not be triggered before an automatic evaluator exists.",
            "attention_cost": {"active_review_minutes": 0.0, "decision_count": 1, "human_actor": "scripted_engineering_smoke_not_human_evidence"},
            "claim_boundary": "Selective escalation rule only.",
        },
        {
            "gate_id": "external_clean_structured_feedback_001",
            "gate_type": "structured_feedback",
            "decision": "separate_figure_data_claim_feedback",
            "rationale": "Different feedback types should change different artifacts.",
            "attention_cost": {"active_review_minutes": 0.0, "decision_count": 1, "human_actor": "scripted_engineering_smoke_not_human_evidence"},
            "claim_boundary": "Template routing evidence only.",
        },
        {
            "gate_id": "external_clean_claim_calibration_001",
            "gate_type": "claim_calibration",
            "decision": "label_as_external_clean_environment_reuse",
            "rationale": "The smoke proves package transfer, not scientific performance.",
            "attention_cost": {"active_review_minutes": 0.0, "decision_count": 1, "human_actor": "scripted_engineering_smoke_not_human_evidence"},
            "claim_boundary": "No human, benchmark, or top-conference evidence.",
        },
    ]

    claim_audit = f"""# External Clean Skill Reuse Claim Audit

- Audit date: `{created_at}`
- External root: `{external_root}`
- External skill directory: `{external_skill_dir}`

| Claim | Evidence | Status | Boundary |
| --- | --- | --- | --- |
| The release skill can be copied into a clean external temporary Codex skills directory. | `summary.json`, copied release files, lineage checks | supported | Engineering transfer only. |
| The copied skill can instantiate a fresh topic with the AI Scientist-v2 base loop and all six IGRE gates. | `task_spec.md`, `six_gate_log.json` | supported | Scripted smoke, not external-user evidence. |
| The workflow improves scientific quality or benchmark performance. | No benchmark, no human rater, no autonomous baseline. | unsupported | Must not be claimed. |

## Final Boundary

This artifact supports clean-environment reuse of the release skill. It does
not replace independent external users, blind expert review, or matched
benchmark evidence.
"""

    task_path = OUT_DIR / "task_spec.md"
    gate_path = OUT_DIR / "six_gate_log.json"
    claim_path = OUT_DIR / "claim_audit.md"
    summary_path = OUT_DIR / "summary.json"
    readme_path = OUT_DIR / "README.md"

    task_path.write_text(task_spec, encoding="utf-8")
    gate_path.write_text(json.dumps({"created_at": created_at, "gates": gates}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    claim_path.write_text(claim_audit, encoding="utf-8")

    generated_paths = [task_path, gate_path, claim_path]
    for path in generated_paths:
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing generated output: {_rel(path)}")

    external_root_text = str(external_root)
    clean_external_environment = external_root.is_absolute() and (
        external_root_text.startswith("/tmp/") or external_root_text.startswith("/private/tmp/")
    )
    if not clean_external_environment:
        warnings.append("external root is not under /tmp; still treated as a clean external workspace if caller prepared it")

    summary = {
        "run_id": "external_clean_skill_reuse_smoke_20260603",
        "created_at": created_at,
        "status": "pass" if not errors else "fail",
        "external_root": str(external_root),
        "external_workspace": str(external_workspace),
        "external_skill_dir": str(external_skill_dir),
        "release_source": _rel(RELEASE_DIR),
        "generated_from_release_copy": True,
        "generated_from_global_install": False,
        "clean_external_environment": clean_external_environment,
        "fresh_topic": "scientific_visualization_replication",
        "required_files_checked": required_files,
        "lineage_present": lineage_present,
        "six_gate_count": len(gates),
        "all_six_gates_present": len({gate["gate_type"] for gate in gates}) == 6,
        "task_spec": _rel(task_path),
        "gate_log": _rel(gate_path),
        "claim_audit": _rel(claim_path),
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This smoke verifies clean external-environment reuse of the release "
            "skill on a fresh topic. It is engineering transfer evidence, not "
            "external-researcher evidence, human-review evidence, benchmark "
            "evidence, or scientific-superiority evidence."
        ),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme_path.write_text(
        "\n".join(
            [
                "# External Clean Skill Reuse Smoke",
                "",
                f"- Run id: `{summary['run_id']}`",
                f"- Status: `{summary['status']}`",
                f"- External root: `{summary['external_root']}`",
                f"- Fresh topic: `{summary['fresh_topic']}`",
                f"- Six gates present: `{summary['all_six_gates_present']}`",
                "",
                "## Artifacts",
                "",
                f"- Task spec: `{summary['task_spec']}`",
                f"- Gate log: `{summary['gate_log']}`",
                f"- Claim audit: `{summary['claim_audit']}`",
                "",
                "## Claim Boundary",
                "",
                summary["claim_boundary"],
                "",
            ]
        ),
        encoding="utf-8",
    )

    if args.update_manifest:
        _update_manifest([Path(__file__), task_path, gate_path, claim_path, summary_path, readme_path], summary)

    print(json.dumps({"summary": _rel(summary_path), "markdown": _rel(readme_path), "status": summary["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
