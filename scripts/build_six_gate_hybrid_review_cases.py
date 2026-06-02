#!/usr/bin/env python3
"""Build six-gate optimized hybrid-review regeneration cases.

The input is raw human peer-review evidence from the deep regeneration case
folders. The output is a deterministic pilot artifact that routes review
signals through six IGRE gates before generating a new mini-paper artifact.
This is a low-cost proxy for the user's proposed experiment; it is not a
substitute for future model-generated reruns or real benchmark execution.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
SOURCE_RUN_ID = "deep_regeneration_cases_20260602_203000"
RUN_ID = "six_gate_hybrid_review_cases_20260602_211500"
SOURCE_DIR = EXP_DIR / SOURCE_RUN_ID
OUT_DIR = EXP_DIR / RUN_ID

GATES = {
    "scientific_taste_prior": {
        "label": "Scientific taste prior",
        "keywords": ["novel", "motivation", "contribution", "impact", "important", "problem", "interesting"],
        "action": "Reweight the research direction toward the most scientifically meaningful problem framing.",
    },
    "evaluator_stress_test": {
        "label": "Evaluator stress test",
        "keywords": ["experiment", "baseline", "metric", "benchmark", "evaluation", "dataset", "ablation"],
        "action": "Add or repair benchmarks, baselines, metrics, and ablations before trusting a result.",
    },
    "frontier_steering": {
        "label": "Frontier steering",
        "keywords": ["generaliz", "scale", "future", "broader", "molecular", "privacy", "refusal", "safety", "unlearning"],
        "action": "Move the follow-up trajectory toward later-relevant concepts and higher-upside branches.",
    },
    "verifiable_micro_evolution": {
        "label": "Verifiable micro-evolution",
        "keywords": ["algorithm", "optimi", "search", "heuristic", "implementation", "gradient", "diffusion", "training"],
        "action": "Identify a machine-gradeable subproblem where OpenEvolve-style search or controlled code improvement is justified.",
    },
    "structured_feedback": {
        "label": "Structured feedback",
        "keywords": ["clarity", "writing", "presentation", "unclear", "structure", "explain", "formulation"],
        "action": "Transform vague feedback into concrete sections, claims, missing definitions, and reader-facing explanations.",
    },
    "claim_calibration": {
        "label": "Claim calibration",
        "keywords": ["limitation", "weakness", "assumption", "generalize", "claim", "overclaim", "boundary"],
        "action": "Narrow unsupported conclusions and state exactly what the current evidence can and cannot prove.",
    },
}


CASE_SPECIFIC_FRONTIER = {
    "openreview_sample_1": [
        "non-arithmetic refusal benchmarks",
        "over-refusal and calibration metrics",
        "user-facing safety or reliability evaluation",
    ],
    "openreview_sample_2": [
        "conditional molecule generation",
        "property satisfaction and validity metrics",
        "baselines that test whether forking is necessary",
    ],
    "openreview_sample_17": [
        "unlearning-set scaling curve",
        "privacy leakage versus retained utility",
        "breaking point of simple unlearning",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _clean_text(value: Any) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _review_texts(human_reviews: dict[str, Any]) -> list[str]:
    texts = []
    for review in human_reviews.get("reviews", []):
        parts = [
            review.get("paper_summary"),
            review.get("main_review"),
            review.get("limitations"),
            review.get("raw"),
        ]
        text = " ".join(_clean_text(part) for part in parts if part)
        if text:
            texts.append(text)
    return texts


def _route_reviews(texts: list[str]) -> dict[str, list[dict[str, str]]]:
    routed = {gate: [] for gate in GATES}
    for text in texts:
        lower = text.lower()
        for gate, spec in GATES.items():
            hits = [keyword for keyword in spec["keywords"] if keyword in lower]
            if hits:
                routed[gate].append(
                    {
                        "matched_keywords": ", ".join(sorted(set(hits))),
                        "evidence_excerpt": text[:700],
                        "gate_action": spec["action"],
                    }
                )
    return routed


def _first_action(routed: dict[str, list[dict[str, str]]], gate: str) -> str:
    actions = routed.get(gate, [])
    if not actions:
        return GATES[gate]["action"]
    return actions[0]["gate_action"]


def _hybrid_review(original: dict[str, Any], regen: dict[str, Any], routed: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    paper_id = original["paper_id"]
    frontier_targets = CASE_SPECIFIC_FRONTIER.get(paper_id, [])
    guided = regen.get("review_guided_regeneration", {})
    return {
        "paper_id": paper_id,
        "title": original.get("title"),
        "six_gate_review": [
            {
                "gate": gate,
                "label": spec["label"],
                "action": _first_action(routed, gate),
                "evidence_count": len(routed.get(gate, [])),
                "evidence": routed.get(gate, [])[:3],
            }
            for gate, spec in GATES.items()
        ],
        "optimized_guidance": {
            "research_question": guided.get("core_contribution") or original.get("abstract_excerpt"),
            "method_change": guided.get("method_sketch"),
            "experiment_change": guided.get("experiment_plan"),
            "frontier_targets": frontier_targets,
            "claim_boundary": guided.get("claim_boundary"),
        },
    }


def _generate_gate_optimized_artifact(original: dict[str, Any], regen: dict[str, Any], hybrid: dict[str, Any]) -> dict[str, Any]:
    guided = regen.get("review_guided_regeneration", {})
    targets = hybrid["optimized_guidance"]["frontier_targets"]
    gate_counts = {item["gate"]: item["evidence_count"] for item in hybrid["six_gate_review"]}
    return {
        "paper_id": original["paper_id"],
        "title": original.get("title"),
        "generation_mode": "deterministic_six_gate_hybrid_review_proxy",
        "core_contribution": guided.get("core_contribution"),
        "six_gate_method_plan": {
            "scientific_taste_prior": "Focus the follow-up on the highest-upside scientific question rather than only polishing the original claim.",
            "evaluator_stress_test": guided.get("experiment_plan"),
            "frontier_steering": targets,
            "verifiable_micro_evolution": "Escalate only if the subproblem has an automatic evaluator and a narrow code or heuristic search space.",
            "structured_feedback": "Rewrite the artifact around problem, method, experiment, limitation, and claim-boundary sections.",
            "claim_calibration": guided.get("claim_boundary"),
        },
        "mini_paper_artifact": (
            f"This six-gate hybrid-review rerun revisits `{original.get('title')}`. "
            f"The human review is not used as raw extra context; it is routed through "
            f"scientific taste, evaluator stress testing, frontier steering, verifiable "
            f"micro-evolution, structured feedback, and claim calibration. The resulting "
            f"research plan keeps the original contribution `{guided.get('core_contribution')}` "
            f"but makes the follow-up test stricter: {guided.get('experiment_plan')} "
            f"The long-horizon branch is steered toward {', '.join(targets) if targets else 'later-field evidence still to be reconstructed'}. "
            f"The claim boundary is: {guided.get('claim_boundary')}"
        ),
        "proxy_metrics": {
            "raw_review_guided_insight_count": len(guided.get("review_insights_used", [])),
            "six_gate_action_count": sum(1 for count in gate_counts.values() if count > 0),
            "total_routed_evidence_count": sum(gate_counts.values()),
            "short_term_gate_support_count": gate_counts.get("evaluator_stress_test", 0)
            + gate_counts.get("structured_feedback", 0)
            + gate_counts.get("claim_calibration", 0),
            "long_horizon_gate_support_count": gate_counts.get("scientific_taste_prior", 0)
            + gate_counts.get("frontier_steering", 0)
            + gate_counts.get("verifiable_micro_evolution", 0),
            "frontier_target_count": len(targets),
        },
        "claim_boundary": (
            "This artifact tests whether six-gate optimization makes review guidance more "
            "actionable. It is not yet a model-generated or benchmark-executed deep rerun."
        ),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_summary = _load_json(SOURCE_DIR / "summary.json")
    outputs = []
    for case in source_summary.get("cases", []):
        source_case_dir = ROOT / case["case_dir"]
        original = _load_json(source_case_dir / "original_paper.json")
        reviews = _load_json(source_case_dir / "human_reviews.json")
        regen = _load_json(source_case_dir / "regenerated_artifacts.json")
        frontier = _load_json(source_case_dir / "future_frontier_evidence.json")
        case_summary = _load_json(source_case_dir / "case_summary.json")
        routed = _route_reviews(_review_texts(reviews))
        hybrid = _hybrid_review(original, regen, routed)
        optimized = _generate_gate_optimized_artifact(original, regen, hybrid)

        out_case_dir = OUT_DIR / Path(case["case_dir"]).name
        out_case_dir.mkdir(parents=True, exist_ok=True)
        _write_json(out_case_dir / "six_gate_routing.json", routed)
        _write_json(out_case_dir / "optimized_hybrid_review.json", hybrid)
        _write_json(out_case_dir / "gate_optimized_regeneration.json", optimized)
        _write_json(
            out_case_dir / "case_comparison.json",
            {
                "paper_id": original["paper_id"],
                "source_case_summary": case_summary,
                "citation_frontier": frontier.get("citation_frontier"),
                "semantic_frontier": frontier.get("semantic_frontier"),
                "gate_optimized_proxy_metrics": optimized["proxy_metrics"],
                "claim_boundary": optimized["claim_boundary"],
            },
        )

        gate_lines = [f"# Six-Gate Hybrid Review: {original.get('title')}", ""]
        for item in hybrid["six_gate_review"]:
            gate_lines.extend(
                [
                    f"## {item['label']}",
                    "",
                    f"- Evidence count: `{item['evidence_count']}`",
                    f"- Optimized action: {item['action']}",
                    "",
                ]
            )
            for evidence in item["evidence"]:
                gate_lines.extend(
                    [
                        f"- Matched keywords: `{evidence['matched_keywords']}`",
                        f"- Evidence excerpt: {evidence['evidence_excerpt']}",
                        "",
                    ]
                )
        _write_md(out_case_dir / "optimized_hybrid_review.md", gate_lines)

        _write_md(
            out_case_dir / "gate_optimized_regeneration.md",
            [
                f"# Gate-Optimized Regeneration: {original.get('title')}",
                "",
                f"- Generation mode: `{optimized['generation_mode']}`",
                "",
                "## Mini-Paper Artifact",
                "",
                optimized["mini_paper_artifact"],
                "",
                "## Proxy Metrics",
                "",
                *[f"- `{key}`: `{value}`" for key, value in optimized["proxy_metrics"].items()],
                "",
                "## Claim Boundary",
                "",
                optimized["claim_boundary"],
            ],
        )
        outputs.append(
            {
                "case_dir": _rel(out_case_dir),
                "paper_id": original["paper_id"],
                "title": original.get("title"),
                "case_type": case_summary.get("case_type"),
                "proxy_metrics": optimized["proxy_metrics"],
            }
        )

    summary = {
        "run_id": RUN_ID,
        "created_at": _utc_now(),
        "status": "six_gate_hybrid_review_proxy_built",
        "source_run_id": SOURCE_RUN_ID,
        "gate_count": len(GATES),
        "gates": list(GATES.keys()),
        "case_count": len(outputs),
        "cases": outputs,
        "claim_boundary": (
            "This experiment optimizes raw human reviews into six-gate hybrid reviews and "
            "generates deterministic mini-paper proxies. It tests workflow structure and "
            "case readiness, not final paper quality or long-horizon superiority."
        ),
    }
    _write_json(OUT_DIR / "summary.json", summary)
    _write_md(
        OUT_DIR / "README.md",
        [
            "# Six-Gate Hybrid Review Cases",
            "",
            f"- Run ID: `{RUN_ID}`",
            f"- Source deep-case run: `{SOURCE_RUN_ID}`",
            f"- Status: `{summary['status']}`",
            f"- Gate count: `{summary['gate_count']}`",
            f"- Case count: `{summary['case_count']}`",
            "",
            "## Gates",
            "",
            *[f"- `{gate}`: {spec['label']}" for gate, spec in GATES.items()],
            "",
            "## Cases",
            "",
            *[
                f"- `{case['paper_id']}`: {case['title']} (`{case['case_dir']}`)"
                for case in outputs
            ],
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
        ],
    )
    print(json.dumps({"run_id": RUN_ID, "summary": _rel(OUT_DIR / "summary.json"), "cases": len(outputs)}, indent=2))


if __name__ == "__main__":
    main()
