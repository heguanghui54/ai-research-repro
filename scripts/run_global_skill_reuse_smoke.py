#!/usr/bin/env python3
"""Use the globally installed Co-Pilot AI Scientist v3 skill on a fresh task."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
OUT_DIR = DOC_DIR / "experiments" / "global_skill_reuse_smoke_20260603"
DEFAULT_SKILL_DIR = Path.home() / ".codex" / "skills" / "co-pilot-ai-scientist-v3"
MANIFEST_PATH = DOC_DIR / "repro_manifest.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _update_manifest(paths: list[Path], summary: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    manifest["global_skill_reuse_smoke"] = {
        "status": summary["status"],
        "output_dir": _rel(OUT_DIR),
        "task_spec": _rel(OUT_DIR / "task_spec.md"),
        "gate_log": _rel(OUT_DIR / "human_gate_log.json"),
        "claim_audit": _rel(OUT_DIR / "claim_audit.md"),
        "base_skill_lineage_checked": summary["base_skill_lineage_checked"],
        "claim_boundary": summary["claim_boundary"],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-dir", default=str(DEFAULT_SKILL_DIR))
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []
    warnings: list[str] = []
    required_global_files = [
        "SKILL.md",
        "MIGRATION.md",
        "templates/task_spec_template.md",
        "templates/human_gate_log_template.json",
        "templates/claim_audit_template.md",
    ]
    for rel in required_global_files:
        path = skill_dir / rel
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing installed skill file: {rel}")

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8") if (skill_dir / "SKILL.md").exists() else ""
    migration_text = (skill_dir / "MIGRATION.md").read_text(encoding="utf-8") if (skill_dir / "MIGRATION.md").exists() else ""
    base_skill_lineage_checked = all(
        term in f"{skill_text}\n{migration_text}"
        for term in [
            "ai-scientist-v2",
            "AI Scientist-v2 research-production loop",
            "scientific_taste_prior",
            "evaluator_stress_test",
            "claim_calibration",
        ]
    )
    if not base_skill_lineage_checked:
        errors.append("installed skill does not expose the expected ai-scientist-v2-to-IGRE lineage")

    created_at = _utc_now()
    task_spec = f"""# Co-Pilot AI Scientist v3 Task Spec

## Research Task ID

`global_skill_reuse_smoke_20260603`

## Topic

Design a small, automatically auditable study of whether review-derived
evaluator-stress gates can prevent metric gaming in a toy tabular ML task. The
task is intentionally outside the existing paper's main replay cases so that it
tests global skill reuse rather than reusing the original package narrative.

## Success Criteria

- Primary benchmark metric: valid-run rate under a guarded evaluator.
- Minimum acceptable improvement: at least one degenerate primary-metric winner
  must be rejected by the evaluator-stress gate in a future executable run.
- Paper-quality target: produce a claim-calibrated mini-report from logs only.
- Reproducibility target: every gate must have a JSON log and every claim must
  cite an artifact path.
- Taste/insight target:
  - The non-metric factor is whether a metric captures the intended scientific
    target rather than merely rewarding a shortcut.
  - A high-tail outcome would be identifying an evaluator flaw before spending
    budget on a misleading branch.

## Failure Criteria

- The evaluator cannot distinguish degenerate shortcuts from valid models.
- The gate changes no control decision and only acts as extra prose.
- No autonomous baseline is available for comparison.

## Human Gates

- `scientific_taste_prior`: keep the task because evaluator reliability is a
  core risk in automated science.
- `long_horizon_taste_gate`: no delayed-value claim in this smoke.
- `evaluator_stress_test`: inspect whether the primary metric can be gamed.
- `frontier_steering`: allocate budget only after the evaluator-stress gate.
- `verifiable_micro_evolution`: trigger only if the evaluator is
  machine-gradeable and has a correctness guardrail.
- `claim_calibration`: report this as global skill reuse evidence only.

## Baselines

- Autonomous AI Scientist-v2 style run: primary metric only.
- Direct LLM rewrite or sampling baseline: not run in this engineering smoke.
- Existing method or benchmark baseline: guarded-evaluator toy baseline.

## Machine-Gradeable Subproblems

- Subproblem: metric-gaming detection for a toy tabular evaluator.
- Evaluator path: to be implemented in a future executable run.
- Initial program path: not applicable for this template smoke.
- OpenEvolve budget: none in this engineering smoke.

## Expected Artifacts

- Human gate logs: `human_gate_log.json`.
- Experiment logs: none; this is a global installed-skill reuse smoke.
- Program-search traces: none.
- Paper draft: none.
- Reproducibility manifest update: `repro_manifest.json`.
"""

    gate_log = {
        "gate_id": "global_skill_reuse_smoke_evaluator_stress_001",
        "gate_type": "evaluator_stress_test",
        "timestamp_utc": created_at,
        "research_task_id": "global_skill_reuse_smoke_20260603",
        "options": [
            {
                "option_id": "primary_metric_only",
                "summary": "Trust the primary score without a guardrail.",
                "score": 0.45,
                "evidence": ["global installed skill template smoke"],
                "risks": ["metric gaming", "false performance improvement"],
            },
            {
                "option_id": "guarded_evaluator",
                "summary": "Require a validity guardrail before optimizing the primary metric.",
                "score": 0.82,
                "evidence": ["IGRE evaluator_stress_test gate design"],
                "risks": ["slower first run", "possible over-filtering"],
            },
        ],
        "human_decision": "guarded_evaluator",
        "rationale": (
            "For an AI Scientist-v2-style loop, an evaluator flaw can invalidate "
            "the whole downstream paper. The global v3 skill therefore routes "
            "this fresh task through evaluator_stress_test before benchmark budget."
        ),
        "affected_artifacts": ["task_spec.md", "claim_audit.md"],
        "downstream_budget": {"future_guarded_evaluator_run": "small toy run only"},
        "attention_cost": {
            "human_actor": "scripted_engineering_smoke_not_human_evidence",
            "interaction_mode": "template_instantiation",
            "prompted_at_utc": created_at,
            "decision_at_utc": created_at,
            "active_review_minutes": 0.0,
            "wall_clock_latency_minutes": 0.0,
            "options_reviewed": 2,
            "artifacts_reviewed_count": 3,
            "decision_count": 1,
            "notes": "Scripted from the globally installed skill; not a live human-subject measurement.",
        },
        "taste_insight": {
            "rubric_version": "2026-06-02",
            "scores": {
                "problem_depth": 3,
                "novelty_potential": 2,
                "mechanistic_value": 3,
                "failure_informativeness": 5,
                "benchmark_taste": 5,
                "claim_significance": 3,
                "risk_asymmetry": 4,
            },
            "taste_insight_score": 3.86,
            "qualitative_rationale": (
                "The useful taste signal is not novelty alone; it is the judgment "
                "that evaluator reliability must be checked before trusting an automated paper loop."
            ),
            "non_metric_factors": ["evaluator_validity", "failure_informativeness", "claim_boundary"],
        },
        "long_horizon_taste_gate": {
            "is_lhtg_candidate": False,
            "dvrs_hypothesis": None,
            "expected_short_term_cost": None,
            "later_field_evidence": [],
            "paper_only_control": None,
            "shuffled_review_control": None,
            "delayed_value_label": "not_evaluated",
            "claim_boundary": "Engineering smoke only; no delayed-value claim.",
        },
        "follow_up_checks": ["Implement guarded evaluator before any performance claim."],
    }

    claim_audit = f"""# Claim Audit

## Manuscript

- Draft path: none
- Audit date: {created_at}
- Reviewer or model route: deterministic global skill reuse smoke

## Claim Table

| Claim | Evidence | Status | Required edit |
| --- | --- | --- | --- |
| The global Co-Pilot AI Scientist v3 skill is installed and can instantiate a fresh task artifact. | `task_spec.md`, `human_gate_log.json`, installed `SKILL.md` and `MIGRATION.md` | supported | Keep as engineering reuse evidence. |
| The generated evaluator-stress gate improves benchmark performance. | No executable benchmark run in this smoke. | remove | Do not make performance claims. |
| The smoke proves human participation improves automated science. | Scripted template instantiation only. | remove | State that this is not human evidence. |

## Unsupported Claims Removed

- Claim: human-gated research is better than autonomous research.
- Reason: this smoke has no autonomous baseline, no benchmark run, and no human expert rating.

## Claims Weakened

- Original: the installed skill works for research.
- Revised: the installed skill can instantiate a fresh task spec, evaluator-stress gate log, and claim audit.
- Evidence: `summary.json` and generated artifacts in this directory.

## Final Gate Decision

- Approve for PDF build: no PDF build involved.
- Remaining risks: future runs still need real benchmarks, autonomous baselines, and human/expert evaluation.
"""

    task_path = OUT_DIR / "task_spec.md"
    gate_path = OUT_DIR / "human_gate_log.json"
    claim_path = OUT_DIR / "claim_audit.md"
    summary_path = OUT_DIR / "summary.json"
    readme_path = OUT_DIR / "README.md"

    task_path.write_text(task_spec, encoding="utf-8")
    gate_path.write_text(json.dumps(gate_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    claim_path.write_text(claim_audit, encoding="utf-8")

    required_outputs = [task_path, gate_path, claim_path]
    for path in required_outputs:
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing generated artifact: {_rel(path)}")

    summary = {
        "run_id": "global_skill_reuse_smoke_20260603",
        "created_at": created_at,
        "status": "pass" if not errors else "fail",
        "skill_dir": str(skill_dir),
        "output_dir": _rel(OUT_DIR),
        "task_spec": _rel(task_path),
        "gate_log": _rel(gate_path),
        "claim_audit": _rel(claim_path),
        "required_global_files_checked": required_global_files,
        "base_skill_lineage_checked": base_skill_lineage_checked,
        "generated_from_global_install": True,
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": (
            "This smoke verifies that the globally installed Co-Pilot AI Scientist "
            "v3 skill can instantiate a fresh research task, gate log, and claim "
            "audit. It is engineering reuse evidence, not benchmark, human, or "
            "scientific-superiority evidence."
        ),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    readme_lines = [
        "# Global Skill Reuse Smoke",
        "",
        f"- Run id: `{summary['run_id']}`",
        f"- Created at: `{summary['created_at']}`",
        f"- Status: `{summary['status']}`",
        f"- Global skill dir: `{summary['skill_dir']}`",
        f"- Base skill lineage checked: `{summary['base_skill_lineage_checked']}`",
        "",
        "## Generated Artifacts",
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
    readme_path.write_text("\n".join(readme_lines), encoding="utf-8")

    if args.update_manifest:
        _update_manifest([Path(__file__), task_path, gate_path, claim_path, summary_path, readme_path], summary)

    print(json.dumps({"summary": _rel(summary_path), "markdown": _rel(readme_path), "status": summary["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
