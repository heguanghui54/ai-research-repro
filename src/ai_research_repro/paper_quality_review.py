from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .llm import chat_json_result


REVIEW_SYSTEM = """You are a demanding but fair ML workshop reviewer.
Review the manuscript against the evidence provided. Be skeptical of overclaims,
leaderboard claims, weak causal claims, missing baselines, reproducibility gaps,
and mismatches between the paper narrative and logged results. Return strict JSON
only, with no markdown fences."""


def _read_text(path: Path, *, max_chars: int = 16000) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-max_chars // 2 :]
    return head + "\n\n[... middle truncated for review prompt ...]\n\n" + tail


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _compact_analysis(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    return {
        "baseline_method": data.get("baseline_method"),
        "model": data.get("model"),
        "role_mode": data.get("role_mode"),
        "task_source": data.get("task_source"),
        "task_count": data.get("task_count"),
        "seeds": data.get("seeds"),
        "best_by_score": data.get("best_by_score"),
        "best_by_score_per_call": data.get("best_by_score_per_call"),
        "methods": data.get("methods", []),
    }


def _compact_audit(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    messages: dict[str, int] = {}
    for finding in data.get("findings", []):
        message = str(finding.get("message", ""))
        messages[message] = messages.get(message, 0) + 1
    top_messages = sorted(messages.items(), key=lambda item: (-item[1], item[0]))[:10]
    return {
        "status": data.get("status"),
        "error_count": data.get("error_count"),
        "warning_count": data.get("warning_count"),
        "top_warning_messages": [{"message": message, "count": count} for message, count in top_messages],
    }


def _compact_svamp(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    return {
        "task": data.get("task"),
        "model": data.get("model"),
        "limit": data.get("limit"),
        "accuracy": data.get("accuracy"),
        "llm_call_count": data.get("llm_call_count"),
        "fallback_calls": data.get("fallback_calls"),
        "usage": data.get("usage"),
        "evaluation_exit_code": data.get("evaluation", {}).get("exit_code"),
        "evaluation_metrics": data.get("evaluation", {}).get("metrics"),
        "wrong_count": sum(1 for row in data.get("rows", []) if not row.get("correct")),
    }


def fallback_paper_quality_review() -> dict[str, Any]:
    return {
        "overall_score": 6.0,
        "recommendation": "revise",
        "summary": "Fallback review: the paper has a reproducible artifact package, but claims should remain narrow until a full external benchmark is run.",
        "scores": {
            "novelty": 6,
            "methodology": 6,
            "evidence_strength": 5,
            "reproducibility": 7,
            "clarity": 6,
            "claim_grounding": 5,
        },
        "strengths": [
            "Includes API-backed experiments, audit artifacts, figures, and a reproducibility checklist.",
            "Separates internal micro-benchmark evidence from AIRS task-local evaluator evidence.",
        ],
        "major_weaknesses": [
            "The official AIRS coverage is partial and should not be framed as a leaderboard result.",
            "Only three seeds are available for the main micro-benchmark, limiting statistical strength.",
        ],
        "minor_weaknesses": [
            "Long paths and tables may be hard to read in PDF form.",
        ],
        "required_revisions": [
            "Keep all broad claims conditional and local to the benchmark scope.",
            "Explicitly state that the SVAMP run is task-local rather than a complete AIRS submission.",
        ],
        "claim_safety": {
            "overclaiming_risk": "medium",
            "unsupported_claims": [],
        },
        "reproducibility": {
            "score": 7,
            "missing_items": ["Full official AIRS harness run."],
        },
        "readiness": "workshop_draft",
    }


def review_paper_quality(
    *,
    paper_path: Path,
    results_dir: Path,
    model: str = "deepseek-chat",
) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    analysis_path = results_dir / "analysis.json"
    audit_path = results_dir / "claim_audit.json"
    figure_critique_path = results_dir / "figure_critique_monica.md"
    svamp_path = Path("runs/airs_svamp_deepseek_submission/deepseek_svamp_submission.json")
    airs12_analysis_path = Path("runs/airs_official_12_deepseek/analysis.json")
    curated_analysis_path = Path("runs/research_external_curated_deepseek/analysis.json")

    if analysis_path.exists():
        evidence["main_analysis"] = _compact_analysis(analysis_path)
    if audit_path.exists():
        evidence["main_claim_audit"] = _compact_audit(audit_path)
    if figure_critique_path.exists():
        evidence["figure_critique_excerpt"] = _read_text(figure_critique_path, max_chars=5000)
    if svamp_path.exists():
        evidence["svamp_task_local_evaluator"] = _compact_svamp(svamp_path)
    if airs12_analysis_path.exists():
        evidence["airs_12_task_planning_subset"] = _compact_analysis(airs12_analysis_path)
    if curated_analysis_path.exists():
        evidence["curated_external_robustness"] = _compact_analysis(curated_analysis_path)

    schema = {
        "overall_score": "number from 0 to 10",
        "recommendation": "accept | weak_accept | revise | reject",
        "summary": "one paragraph",
        "scores": {
            "novelty": "0-10",
            "methodology": "0-10",
            "evidence_strength": "0-10",
            "reproducibility": "0-10",
            "clarity": "0-10",
            "claim_grounding": "0-10",
        },
        "strengths": ["specific strength"],
        "major_weaknesses": ["specific weakness"],
        "minor_weaknesses": ["specific weakness"],
        "required_revisions": ["actionable revision"],
        "claim_safety": {
            "overclaiming_risk": "low | medium | high",
            "unsupported_claims": ["quote or paraphrase of risky claim"],
        },
        "reproducibility": {
            "score": "0-10",
            "missing_items": ["missing item"],
        },
        "readiness": "workshop_draft | near_submission | not_ready",
    }
    user = f"""Review this autonomous-AI-research manuscript as a rigorous ML workshop reviewer.

MANUSCRIPT:
{_read_text(paper_path, max_chars=28000)}

EVIDENCE SUMMARY:
{json.dumps(evidence, indent=2)}

Return JSON matching this schema:
{json.dumps(schema, indent=2)}
"""
    result = chat_json_result(system=REVIEW_SYSTEM, user=user, model=model, fallback=fallback_paper_quality_review)
    review = result.parsed if isinstance(result.parsed, dict) else fallback_paper_quality_review()
    review.setdefault("meta", {})
    review["meta"].update(
        {
            "paper_path": str(paper_path),
            "results_dir": str(results_dir),
            "model": model,
            "llm_meta": result.meta or {},
        }
    )
    return review


def review_to_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# Paper Quality Review",
        "",
        f"- Overall score: {review.get('overall_score', '')}",
        f"- Recommendation: {review.get('recommendation', '')}",
        f"- Readiness: {review.get('readiness', '')}",
        f"- Overclaiming risk: {review.get('claim_safety', {}).get('overclaiming_risk', '')}",
        "",
        "## Summary",
        "",
        str(review.get("summary", "")),
        "",
        "## Scores",
        "",
    ]
    scores = review.get("scores", {})
    if isinstance(scores, dict):
        for key, value in scores.items():
            lines.append(f"- {key}: {value}")
    for section in ["strengths", "major_weaknesses", "minor_weaknesses", "required_revisions"]:
        lines.extend(["", f"## {section.replace('_', ' ').title()}", ""])
        items = review.get(section, [])
        if not items:
            lines.append("- None reported.")
        else:
            for item in items:
                lines.append(f"- {item}")
    lines.extend(["", "## Claim Safety", ""])
    claim_safety = review.get("claim_safety", {})
    unsupported = claim_safety.get("unsupported_claims", []) if isinstance(claim_safety, dict) else []
    for item in unsupported:
        lines.append(f"- {item}")
    if not unsupported:
        lines.append("- None reported.")
    lines.extend(["", "## Reproducibility", ""])
    repro = review.get("reproducibility", {})
    if isinstance(repro, dict):
        lines.append(f"- Score: {repro.get('score', '')}")
        for item in repro.get("missing_items", []):
            lines.append(f"- Missing: {item}")
    return "\n".join(lines).rstrip() + "\n"


def save_paper_quality_review(review: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "paper_quality_review.json"
    md_path = output_dir / "paper_quality_review.md"
    json_path.write_text(json.dumps(review, indent=2), encoding="utf-8")
    md_path.write_text(review_to_markdown(review), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}
