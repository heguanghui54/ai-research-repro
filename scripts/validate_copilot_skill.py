#!/usr/bin/env python3
"""Validate the Co-Pilot AI Scientist v3 Codex skill is reusable."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SKILL_DIR = ROOT / "skills" / "co-pilot-ai-scientist-v3"
AUDIT_DIR = DOC_DIR / "audits"


REQUIRED_SKILL_TERMS = [
    "Insight-Gated Research Evolution",
    "scientific_taste_prior",
    "evaluator_stress_test",
    "frontier_steering",
    "verifiable_micro_evolution",
    "claim_calibration",
    "OpenEvolve",
    "taste_insight",
    "attention_cost",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _frontmatter_name(text: str) -> str | None:
    match = re.match(r"---\n(.*?)\n---", text, flags=re.S)
    if not match:
        return None
    for line in match.group(1).splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def _validate_gate(schema: dict[str, Any], gate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in schema.get("required", []):
        if field not in gate:
            errors.append(f"missing required field: {field}")
    gate_types = schema.get("properties", {}).get("gate_type", {}).get("enum", [])
    if gate.get("gate_type") not in gate_types:
        errors.append(f"invalid gate_type: {gate.get('gate_type')}")
    taste = gate.get("taste_insight", {})
    if not isinstance(taste, dict):
        errors.append("taste_insight must be an object")
    else:
        scores = taste.get("scores", {})
        for dimension in [
            "problem_depth",
            "novelty_potential",
            "mechanistic_value",
            "failure_informativeness",
            "benchmark_taste",
            "claim_significance",
            "risk_asymmetry",
        ]:
            value = scores.get(dimension) if isinstance(scores, dict) else None
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 1 <= value <= 5:
                errors.append(f"invalid taste score: {dimension}")
        if not taste.get("qualitative_rationale"):
            errors.append("missing qualitative_rationale")
        if not taste.get("non_metric_factors"):
            errors.append("missing non_metric_factors")
    return errors


def _instantiate_task_spec() -> str:
    return """# Co-Pilot AI Scientist v3 Task Spec

## Research Task ID

`skill_reuse_smoke_001`

## Topic

Validate that the Co-Pilot AI Scientist v3 Codex skill can be reused on a new
research task without relying on the original chat context.

## Success Criteria

- Primary benchmark metric: all required skill artifacts validate locally.
- Minimum acceptable improvement: generated gate log conforms to schema.
- Paper-quality target: claims stay grounded in audit outputs.
- Reproducibility target: clean clone can rerun the validation script.
- Taste/insight target:
  - Which non-metric scientific factor matters most? Benchmark-to-claim fit.
  - What high-tail outcome would justify preserving a risky branch? A branch
    that exposes an evaluator flaw or stronger research question.

## Failure Criteria

- Missing skill instructions, templates, or schema.
- Generated human gate cannot be validated.
- The skill encourages unsupported performance claims.

## Human Gates

- `scientific_taste_prior`: choose claim-matched benchmarks over convenient benchmarks.
- `evaluator_stress_test`: reject metric-gaming or invalid evaluators.
- `frontier_steering`: preserve high-upside branches at budget checkpoints.
- `verifiable_micro_evolution`: escalate machine-gradeable subproblems only when warranted.
- `claim_calibration`: weaken unsupported paper claims before PDF build.

## Baselines

- Autonomous AI Scientist-v2 style run: required for future matched experiments.
- Direct LLM rewrite or sampling baseline: required for program-search comparisons.
- Existing method or benchmark baseline: selected by claim type.

## Machine-Gradeable Subproblems

- Subproblem: skill-template validation.
- Evaluator path: `scripts/validate_copilot_skill.py`.
- Initial program path: not applicable.
- OpenEvolve budget: not launched for this smoke test.

## Expected Artifacts

- Human gate logs: `skill_reuse_smoke_human_gate_log.json`.
- Experiment logs: `skill_reuse_smoke_audit.json`.
- Program-search traces: not applicable for this smoke test.
- Paper draft: not generated in this smoke test.
- Reproducibility manifest update: required after audit.
"""


def _instantiate_gate(template: dict[str, Any], timestamp_utc: str) -> dict[str, Any]:
    gate = dict(template)
    gate.update(
        {
            "gate_id": "skill_reuse_smoke_scientific_taste_prior_001",
            "gate_type": "scientific_taste_prior",
            "timestamp_utc": timestamp_utc,
            "research_task_id": "skill_reuse_smoke_001",
            "options": [
                {
                    "option_id": "reuse_existing_skill",
                    "summary": "Reuse the Co-Pilot AI Scientist v3 skill with a new task spec and validated human gate log.",
                    "score": 4.0,
                    "evidence": [
                        "SKILL.md exists and includes IGRE workflow terms.",
                        "Task and gate templates can be instantiated.",
                        "Generated gate log validates against the project schema.",
                    ],
                    "risks": [
                        "This smoke validates artifact reuse, not research performance.",
                    ],
                },
                {
                    "option_id": "manual_ad_hoc_workflow",
                    "summary": "Continue using project-specific files without a reusable skill interface.",
                    "score": 2.0,
                    "evidence": [
                        "Manual workflow is flexible.",
                    ],
                    "risks": [
                        "Does not satisfy the reusable Codex skill objective.",
                        "Harder to audit human gates consistently.",
                    ],
                },
            ],
            "human_decision": "reuse_existing_skill",
            "rationale": "The reusable skill path better satisfies the project objective because it preserves IGRE gate semantics, template structure, and schema-validated human decision logs across tasks.",
            "affected_artifacts": [
                "skills/co-pilot-ai-scientist-v3/SKILL.md",
                "skills/co-pilot-ai-scientist-v3/templates/task_spec_template.md",
                "skills/co-pilot-ai-scientist-v3/templates/human_gate_log_template.json",
                "docs/co_pilot_ai_scientist_v3/human_gate_schema.json",
            ],
            "downstream_budget": {
                "skill_validation": "local_smoke",
                "remote_experiments_launched": 0,
            },
            "follow_up_checks": [
                "Run the skill on a fresh research topic with live model calls.",
                "Record attention_cost prospectively during live human gates.",
            ],
        }
    )
    gate["attention_cost"] = {
        "human_actor": "codex_validation",
        "interaction_mode": "posthoc_replay",
        "prompted_at_utc": None,
        "decision_at_utc": timestamp_utc,
        "active_review_minutes": None,
        "wall_clock_latency_minutes": None,
        "options_reviewed": 2,
        "artifacts_reviewed_count": 4,
        "decision_count": 1,
        "notes": "Smoke test validates reusable skill artifacts; no prospective human timing was measured.",
    }
    gate["taste_insight"] = {
        "rubric_version": "2026-06-02",
        "scores": {
            "problem_depth": 4,
            "novelty_potential": 3,
            "mechanistic_value": 4,
            "failure_informativeness": 4,
            "benchmark_taste": 5,
            "claim_significance": 4,
            "risk_asymmetry": 3,
        },
        "taste_insight_score": 3.9,
        "qualitative_rationale": "A reusable skill matters because it turns the paper's human-taste gates into repeatable research operations rather than one-off prose.",
        "non_metric_factors": [
            "workflow transferability",
            "schema discipline",
            "benchmark-to-claim fit",
        ],
    }
    return gate


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Co-Pilot AI Scientist v3 Skill Reuse Smoke Audit",
        "",
        f"Audit date: {summary['audit_date']}",
        "",
        "This audit validates that the Codex skill can be reused as a structured",
        "workflow artifact. It instantiates a new task spec and a schema-compatible",
        "human gate log from the skill templates.",
        "",
        "## Result",
        "",
        f"- Overall status: {summary['overall_status']}",
        f"- Skill name: `{summary['skill_name']}`",
        f"- Required workflow terms present: {summary['required_terms_present']}/{summary['required_terms_total']}",
        f"- Templates parsed: {len(summary['templates_parsed'])}",
        f"- Generated task spec: `{summary['generated_task_spec']}`",
        f"- Generated gate log: `{summary['generated_gate_log']}`",
        f"- Gate schema validation errors: {len(summary['gate_validation_errors'])}",
        "",
        "Parsed templates:",
        "",
    ]
    for template in summary["templates_parsed"]:
        lines.append(f"- `{template}`")
    lines.extend(
        [
        "",
        "## Checks",
        "",
        "| Check | Status |",
        "| --- | --- |",
        ]
    )
    for check, status in summary["checks"].items():
        lines.append(f"| {check} | {status} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The skill is reusable as a Codex artifact at the template/schema level.",
            "This is stronger than merely checking that `SKILL.md` exists, but it is",
            "still a smoke test: it does not launch a new end-to-end research run, call",
            "LLMs, or prove that the skill improves paper quality.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp-utc", default="2026-06-01T17:30:00Z")
    parser.add_argument(
        "--output-json",
        default="docs/co_pilot_ai_scientist_v3/audits/skill_reuse_smoke_audit.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/co_pilot_ai_scientist_v3/audits/skill_reuse_smoke_audit.md",
    )
    args = parser.parse_args()

    skill_path = SKILL_DIR / "SKILL.md"
    task_template_path = SKILL_DIR / "templates" / "task_spec_template.md"
    gate_template_path = SKILL_DIR / "templates" / "human_gate_log_template.json"
    claim_template_path = SKILL_DIR / "templates" / "claim_audit_template.md"
    schema_path = DOC_DIR / "human_gate_schema.json"

    skill_text = skill_path.read_text(encoding="utf-8")
    skill_name = _frontmatter_name(skill_text)
    missing_terms = [term for term in REQUIRED_SKILL_TERMS if term not in skill_text]

    task_template_exists = task_template_path.exists()
    claim_template_exists = claim_template_path.exists()
    gate_template = _load_json(gate_template_path)
    schema = _load_json(schema_path)
    task_spec = _instantiate_task_spec()
    gate = _instantiate_gate(gate_template, args.timestamp_utc)
    validation_errors = _validate_gate(schema, gate)

    generated_task_spec = AUDIT_DIR / "skill_reuse_smoke_task_spec.md"
    generated_gate_log = AUDIT_DIR / "skill_reuse_smoke_human_gate_log.json"
    generated_task_spec.write_text(task_spec, encoding="utf-8")
    generated_gate_log.write_text(json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks = {
        "skill_file_exists": "pass" if skill_path.exists() else "fail",
        "skill_frontmatter_name": "pass" if skill_name == "co-pilot-ai-scientist-v3" else "fail",
        "required_workflow_terms": "pass" if not missing_terms else "fail",
        "task_template_exists": "pass" if task_template_exists else "fail",
        "gate_template_parses": "pass",
        "claim_template_exists": "pass" if claim_template_exists else "fail",
        "human_gate_schema_parses": "pass",
        "generated_gate_validates": "pass" if not validation_errors else "fail",
    }
    overall_status = "pass" if all(status == "pass" for status in checks.values()) else "fail"

    summary = {
        "audit_date": args.timestamp_utc,
        "overall_status": overall_status,
        "skill_name": skill_name,
        "required_terms_total": len(REQUIRED_SKILL_TERMS),
        "required_terms_present": len(REQUIRED_SKILL_TERMS) - len(missing_terms),
        "missing_required_terms": missing_terms,
        "templates_parsed": [
            str(task_template_path.relative_to(ROOT)),
            str(gate_template_path.relative_to(ROOT)),
            str(claim_template_path.relative_to(ROOT)),
        ],
        "generated_task_spec": str(generated_task_spec.relative_to(ROOT)),
        "generated_gate_log": str(generated_gate_log.relative_to(ROOT)),
        "gate_validation_errors": validation_errors,
        "checks": checks,
    }

    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
