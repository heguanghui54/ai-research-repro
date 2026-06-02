#!/usr/bin/env python3
"""Build preregistered replay specs for delayed-value deep cases."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
SOURCE_RUN = EXP_DIR / "delayed_value_deep_case_triage_20260602_232000"
RUN_ID = "delayed_value_replay_specs_20260602_234500"
OUT_DIR = EXP_DIR / RUN_ID

CONDITIONS = [
    "paper_only",
    "raw_review_guided",
    "six_gate_hybrid_guided",
    "shuffled_review_control",
]


CASE_PROTOCOLS = {
    "paper_132_review_2": {
        "domain": "deep_learning_theory",
        "replay_question": (
            "Can human review emphasizing generalization and theory steer an automated "
            "researcher from a narrow NTK-rate result toward a more frontier-aligned "
            "study of averaged SGD, finite-width effects, and generalization mechanisms?"
        ),
        "minimal_experiment": [
            "Generate a follow-up theorem-or-experiment plan for averaged SGD under NTK-like assumptions.",
            "Require at least one stress test outside the exact assumptions of the original proof.",
            "Compare the generated plan against later frontier descriptors around generalization, finite-width behavior, and optimization dynamics.",
        ],
        "short_term_metrics": [
            "technical correctness of proposed theorem/experiment",
            "clarity of assumptions",
            "baseline and prior-work calibration",
        ],
        "frontier_metrics": [
            "alignment with later generalization and finite-width NTK themes",
            "mechanistic depth beyond restating the original rate result",
            "specificity of testable predictions",
        ],
        "failure_modes": [
            "generic theory praise without a new stress test",
            "overclaiming beyond the original assumptions",
            "frontier alignment driven only by title terms such as neural or generalization",
        ],
    },
    "paper_105_review_1": {
        "domain": "medical_image_segmentation",
        "replay_question": (
            "Can review comments about efficiency, dynamic sparse feature fusion, and mechanism "
            "turn an automated follow-up into a stronger study of efficient 3D medical segmentation "
            "under deployment constraints?"
        ),
        "minimal_experiment": [
            "Generate a compact 3D segmentation follow-up with an explicit efficiency/accuracy tradeoff.",
            "Require at least one ablation of the sparse fusion mechanism and one deployment-oriented metric.",
            "Compare against later frontier descriptors around efficient 3D segmentation, transformers, U-Net variants, and clinical constraints.",
        ],
        "short_term_metrics": [
            "plausibility of architecture changes",
            "quality of ablation plan",
            "claim calibration around dataset and deployment limits",
        ],
        "frontier_metrics": [
            "alignment with efficient 3D medical segmentation trends",
            "mechanistic explanation of sparse feature fusion",
            "resource-aware evaluation specificity",
        ],
        "failure_modes": [
            "architecture shopping without a mechanism",
            "accuracy-only evaluation",
            "clinical or deployment claims without data",
        ],
    },
    "paper_37_review_1": {
        "domain": "causal_generalization",
        "replay_question": (
            "Can human taste around causal structure and distribution shift steer an automated "
            "researcher from weighted representations toward a stronger study of treatment-effect "
            "generalization across changing designs?"
        ),
        "minimal_experiment": [
            "Generate a follow-up causal inference experiment with train/test design shift.",
            "Require a paper-only, review-guided, and control plan to specify covariate shift, treatment-policy shift, and outcome-model shift separately.",
            "Compare against later frontier descriptors around causal representation learning, domain generalization, and robust policy evaluation.",
        ],
        "short_term_metrics": [
            "identification clarity",
            "baseline choice under design shift",
            "specificity of synthetic or semi-synthetic benchmark",
        ],
        "frontier_metrics": [
            "alignment with causal representation and domain generalization themes",
            "explicit handling of policy/design shift",
            "quality of failure-mode analysis",
        ],
        "failure_modes": [
            "confusing prediction generalization with causal identification",
            "using generic domain adaptation language without treatment-effect metrics",
            "review guidance improving prose but not the causal experiment",
        ],
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _condition_prompt(case: dict[str, Any], protocol: dict[str, Any], condition: str) -> str:
    shared = f"""You are running a Temporal Frontier Replay experiment for Co-Pilot AI Scientist v3.

Original paper title: {case['title']}
Domain: {protocol['domain']}
Replay question: {protocol['replay_question']}

Original review excerpt available to this spec:
{case.get('excerpt', '')}

Required output:
- a concise research hypothesis;
- a minimal experiment or theorem plan;
- expected baselines;
- evaluation metrics;
- one ablation or stress test;
- failure modes;
- claim boundaries.

Do not invent completed results. Write a plan that could be executed under a small research budget.
"""
    if condition == "paper_only":
        guidance = (
            "Condition: paper_only. Use only the paper title and neutral paper context. "
            "Do not use the human review as guidance, except that it is shown above for logging and must be ignored."
        )
    elif condition == "raw_review_guided":
        guidance = (
            "Condition: raw_review_guided. Use the human review excerpt directly as guidance. "
            "Do not restructure it into gates."
        )
    elif condition == "six_gate_hybrid_guided":
        gates = ", ".join(case.get("primary_gates") or [])
        long_groups = ", ".join(case.get("long_horizon_groups") or [])
        friction = ", ".join(case.get("friction_groups") or [])
        guidance = f"""Condition: six_gate_hybrid_guided. Convert the review into IGRE gate actions before proposing the follow-up.

Primary gates from triage: {gates}
Long-horizon groups: {long_groups}
Productive friction: {friction}

Required gate routing:
- scientific_taste_prior: identify the non-obvious taste/insight in the review;
- evaluator_stress_test: specify what metric or benchmark could expose a weak claim;
- frontier_steering: state how the follow-up could align with later field movement;
- verifiable_micro_evolution: name one bounded code, proof, or evaluator subproblem to improve automatically;
- structured_feedback: rewrite vague review advice into concrete actions;
- claim_calibration: state what the generated follow-up must not claim.
"""
    elif condition == "shuffled_review_control":
        guidance = (
            "Condition: shuffled_review_control. Use a same-length but unrelated peer-review style control. "
            "The control should preserve generic reviewer pressure while removing paper-specific taste."
        )
    else:
        raise ValueError(condition)

    metrics = "\n".join(f"- {metric}" for metric in protocol["short_term_metrics"] + protocol["frontier_metrics"])
    failures = "\n".join(f"- {mode}" for mode in protocol["failure_modes"])
    return f"""{shared}
{guidance}

Scoring metrics to satisfy:
{metrics}

Known failure modes:
{failures}
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    selected = _load_json(SOURCE_RUN / "selected_cases.json")
    case_records = []

    for case in selected:
        review_id = case["review_id"]
        protocol = CASE_PROTOCOLS[review_id]
        case_dir = OUT_DIR / review_id
        case_dir.mkdir(parents=True, exist_ok=True)

        spec = {
            "run_id": RUN_ID,
            "review_id": review_id,
            "title": case["title"],
            "domain": protocol["domain"],
            "candidate_label": case.get("candidate_label"),
            "triage_score": case.get("triage_score"),
            "source_triage": _rel(SOURCE_RUN / "selected_cases.json"),
            "replay_question": protocol["replay_question"],
            "required_conditions": CONDITIONS,
            "minimal_experiment": protocol["minimal_experiment"],
            "short_term_metrics": protocol["short_term_metrics"],
            "frontier_metrics": protocol["frontier_metrics"],
            "failure_modes": protocol["failure_modes"],
            "primary_gates": case.get("primary_gates"),
            "long_horizon_groups": case.get("long_horizon_groups"),
            "friction_groups": case.get("friction_groups"),
            "review_signal": case.get("review_signal"),
            "title_signal": case.get("title_signal"),
            "selection_reasons": case.get("selection_reasons"),
            "required_artifacts_after_execution": [
                "paper_only_plan.md",
                "raw_review_guided_plan.md",
                "six_gate_hybrid_guided_plan.md",
                "shuffled_review_control_plan.md",
                "condition_scores.json",
                "frontier_alignment_judgement.json",
                "case_analysis.md",
            ],
            "positive_delayed_value_rule": [
                "raw_review_guided or six_gate_hybrid_guided has lower short_term_score than paper_only",
                "the same guided condition has higher frontier_alignment_score than paper_only",
                "the same guided condition beats shuffled_review_control on frontier_alignment_score",
                "the responsible review signal is specific and actionable",
                "later-frontier evidence passes bibliographic and semantic match guards",
            ],
            "claim_boundary": (
                "This is a preregistered replay specification. It is not an executed replay and "
                "must not be counted as evidence that human review improves research output."
            ),
        }
        (case_dir / "replay_spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for condition in CONDITIONS:
            (case_dir / f"{condition}_prompt.txt").write_text(
                _condition_prompt(case, protocol, condition),
                encoding="utf-8",
            )

        md = [
            f"# Replay Spec: {case['title']}",
            "",
            f"- Review ID: `{review_id}`",
            f"- Domain: `{protocol['domain']}`",
            f"- Candidate label: `{case.get('candidate_label')}`",
            f"- Triage score: `{case.get('triage_score')}`",
            f"- Required conditions: `{', '.join(CONDITIONS)}`",
            "",
            "## Replay Question",
            "",
            protocol["replay_question"],
            "",
            "## Minimal Experiment",
            "",
        ]
        md.extend(f"- {item}" for item in protocol["minimal_experiment"])
        md.extend(["", "## Short-Term Metrics", ""])
        md.extend(f"- {item}" for item in protocol["short_term_metrics"])
        md.extend(["", "## Frontier Metrics", ""])
        md.extend(f"- {item}" for item in protocol["frontier_metrics"])
        md.extend(["", "## Failure Modes", ""])
        md.extend(f"- {item}" for item in protocol["failure_modes"])
        md.extend(["", "## Positive Delayed-Value Rule", ""])
        md.extend(f"- {item}" for item in spec["positive_delayed_value_rule"])
        md.extend(["", "## Claim Boundary", "", spec["claim_boundary"], ""])
        (case_dir / "replay_spec.md").write_text("\n".join(md), encoding="utf-8")

        case_records.append(
            {
                "review_id": review_id,
                "title": case["title"],
                "domain": protocol["domain"],
                "case_dir": _rel(case_dir),
                "triage_score": case.get("triage_score"),
                "required_conditions": CONDITIONS,
            }
        )

    summary = {
        "run_id": RUN_ID,
        "timestamp_utc": _utc_now(),
        "status": "preregistered_replay_specs_only",
        "source_triage_run": _rel(SOURCE_RUN),
        "case_count": len(case_records),
        "conditions": CONDITIONS,
        "cases": case_records,
        "claim_boundary": (
            "The specs make the next delayed-value replay executable and auditable. "
            "They do not contain generated papers, benchmark results, or human expert ratings."
        ),
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Delayed-Value Replay Specs",
        "",
        f"- Run ID: `{RUN_ID}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Source triage: `{summary['source_triage_run']}`",
        f"- Case count: `{summary['case_count']}`",
        f"- Conditions: `{', '.join(CONDITIONS)}`",
        "",
        "## Cases",
        "",
        "| Case | Domain | Triage | Required conditions |",
        "| --- | --- | ---: | --- |",
    ]
    for case in case_records:
        lines.append(
            f"| `{case['review_id']}` {case['title']} | `{case['domain']}` | "
            f"{case['triage_score']} | `{', '.join(case['required_conditions'])}` |"
        )
    lines.extend(
        [
            "",
            "## Execution Boundary",
            "",
            summary["claim_boundary"],
            "",
            "## Required Per-Case Files",
            "",
            "Each case folder contains `replay_spec.json`, `replay_spec.md`, and one prompt per condition. After execution, the folder should be extended with condition plans, condition scores, frontier judgements, and case analysis.",
            "",
        ]
    )
    (OUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"run_id": RUN_ID, "summary": _rel(OUT_DIR / "summary.json"), "case_count": len(case_records)}, indent=2))


if __name__ == "__main__":
    main()
