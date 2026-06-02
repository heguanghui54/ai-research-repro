#!/usr/bin/env python3
"""Mine review snippets for citation-backed future-frontier signals.

This probe asks a narrower question than the regenerated-artifact probes:
do historical human reviews contain terms or control suggestions that align
with later citing-paper frontiers, even when the regenerated artifact does not?

It is deliberately lexical and conservative. It should be read as a
screening tool for candidate human taste/insight signals, not as proof that
the reviews caused later research trajectories.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SOURCE_DIR = DOC_DIR / "experiments" / "openreview_guided_regeneration_probe_20260602_073500"

STOPWORDS = {
    "about", "across", "also", "and", "are", "author", "authors", "based",
    "been", "better", "between", "can", "contribution", "could", "dataset",
    "datasets", "deep", "different", "does", "empirical", "evaluate",
    "evaluation", "experiment", "experiments", "for", "from", "have", "how",
    "however", "important", "including", "large", "learning", "method",
    "methods", "model", "models", "more", "not", "novel", "one", "our",
    "over", "paper", "performance", "propose", "proposed", "provide",
    "review", "reviewer", "result", "results", "should", "show", "shows",
    "study", "task", "tasks", "that", "the", "their", "these", "this",
    "through", "use", "used", "using", "well", "were", "which", "with",
    "work", "would",
}

ACTIONABILITY_TERMS = {
    "ablation", "baseline", "benchmark", "calibration", "causal",
    "comparison", "dataset", "evaluation", "metric", "privacy", "robustness",
    "safety", "scaling", "uncertainty",
}

GATE_PATTERNS = {
    "scientific_taste_prior": [
        r"\bnovel\b", r"\bincremental\b", r"\bimpact\b", r"\bimportant\b",
        r"\bpromising\b", r"\binteresting\b", r"\bprior work\b",
    ],
    "evaluator_stress_test": [
        r"\bevaluation\b", r"\bexperiment", r"\bbenchmark\b", r"\bbaseline\b",
        r"\bablation\b", r"\bmetric\b", r"\bdataset\b", r"\bcomparison\b",
        r"\bcorrect", r"\bassumption\b", r"\bvalid",
    ],
    "frontier_steering": [
        r"\bfuture work\b", r"\bextension\b", r"\bfurther\b", r"\bgo further\b",
        r"\bpromising\b", r"\bimportant problem\b",
    ],
    "structured_feedback": [
        r"\bclarity\b", r"\bunclear\b", r"\bwriting\b", r"\bpresentation\b",
        r"\borganization\b", r"\bexplain", r"\bdefinition\b", r"\bcode\b",
        r"\breproduc",
    ],
    "claim_calibration": [
        r"\blimitation", r"\bweakness", r"\bclaim", r"\boverclaim",
        r"\bunsupported", r"\binsufficient", r"\bconcern", r"\bfailure",
    ],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _tokens(text: str) -> list[str]:
    tokens = []
    for token in re.findall(r"[a-z][a-z0-9\-]{2,}", text.lower()):
        if token.endswith("s") and len(token) > 4:
            token = token[:-1]
        if token not in STOPWORDS and not token.isdigit():
            tokens.append(token)
    return tokens


def _flatten_review(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    parts: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(data)
    return "\n".join(parts)


def _score_text(text: str, frontier_terms: list[str]) -> dict[str, Any]:
    token_set = set(_tokens(text))
    matched_frontier = [term for term in frontier_terms if term in token_set]
    matched_action = sorted(ACTIONABILITY_TERMS & token_set)
    frontier_alignment = len(matched_frontier) / len(frontier_terms) if frontier_terms else 0.0
    actionability = min(1.0, len(matched_action) / 5)
    score = (0.75 * frontier_alignment) + (0.25 * actionability)
    return {
        "score": round(score, 4),
        "frontier_alignment": round(frontier_alignment, 4),
        "actionability": round(actionability, 4),
        "matched_frontier_terms": matched_frontier,
        "matched_actionability_terms": matched_action,
    }


def _route_gate(text: str) -> str:
    counts = {}
    for gate, patterns in GATE_PATTERNS.items():
        counts[gate] = sum(1 for pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE))
    best_gate, best_count = max(counts.items(), key=lambda item: item[1])
    if best_count == 0:
        return "triage_before_gate"
    return best_gate


def _best(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not items:
        return None
    return max(items, key=lambda item: item["frontier_signal"]["score"])


def _markdown(summary: dict[str, Any]) -> str:
    aggregate = summary["aggregate"]
    lines = [
        "# Review Frontier Signal Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Citation frontier source: `{summary['citation_frontier_source']}`",
        "",
        "## Aggregate",
        "",
        f"- Papers evaluated: `{aggregate['paper_count']}`",
        f"- Papers with frontier terms: `{aggregate['papers_with_frontier_terms']}`",
        f"- Review snippets scored: `{aggregate['review_snippet_count']}`",
        f"- Review beats paper-context cases: `{aggregate['review_beats_paper_context_count']}`",
        f"- Review beats generated artifact cases: `{aggregate['review_beats_review_guided_artifact_count']}`",
        f"- Latent delayed-value candidate cases: `{aggregate['latent_delayed_value_candidate_count']}`",
        f"- Mean best-review score: `{aggregate['mean_best_review_score']}`",
        f"- Mean paper-context score: `{aggregate['mean_paper_context_score']}`",
        f"- Mean review-guided-artifact score: `{aggregate['mean_review_guided_artifact_score']}`",
        f"- Best-review gate counts: `{json.dumps(aggregate['best_review_gate_counts'], sort_keys=True)}`",
        "",
        "## Per Paper",
        "",
    ]
    for item in summary["per_paper"]:
        best = item["best_review_snippet"]
        best_view = best["frontier_signal"]["score"] if best else None
        lines.append(
            f"- `{item['paper_id']}`: frontier quality `{item['frontier_quality']}`; "
            f"paper context `{item['paper_context_signal']['score']}`; "
            f"review-guided artifact `{item['review_guided_artifact_signal']['score']}`; "
            f"best review `{best_view}` via `{best['gate'] if best else 'none'}`; "
            f"pattern `{item['interpretation']['pattern']}`"
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--citation-summary", required=True)
    parser.add_argument("--run-id", default="review_frontier_signal_probe_20260602_214500")
    args = parser.parse_args()

    citation_path = Path(args.citation_summary)
    if not citation_path.is_absolute():
        citation_path = ROOT / citation_path
    citation_summary = _load_json(citation_path)
    selected = {item["paper_id"]: item for item in _load_json(SOURCE_DIR / "selected_papers.json")}
    regenerated = {
        item["paper_id"]: item
        for item in _load_json(SOURCE_DIR / "regenerated_artifacts.json")["papers"]
    }
    local_quality = {
        item["paper_id"]: item
        for item in _load_json(SOURCE_DIR / "summary.json")["scoring"]["per_paper"]
    }

    per_paper = []
    for frontier_row in citation_summary["per_paper"]:
        paper_id = frontier_row["paper_id"]
        paper = selected[paper_id]
        terms = frontier_row.get("frontier_terms") or []
        paper_context = "\n".join([
            paper.get("title") or "",
            paper.get("abstract_excerpt") or "",
            paper.get("decision_text_excerpt") or "",
        ])
        paper_signal = _score_text(paper_context, terms)
        review_artifact_text = "\n".join(
            str(regenerated[paper_id]["review_guided_regeneration"].get(key) or "")
            for key in [
                "core_contribution", "method_sketch", "experiment_plan",
                "limitations", "claim_boundary", "mini_paper_artifact",
            ]
        )
        artifact_signal = _score_text(review_artifact_text, terms)
        scored_reviews = []
        for idx, raw in enumerate(paper.get("review_snippets") or []):
            text = _flatten_review(raw)
            scored_reviews.append(
                {
                    "review_index": idx,
                    "gate": _route_gate(text),
                    "frontier_signal": _score_text(text, terms),
                    "excerpt": re.sub(r"\s+", " ", text).strip()[:700],
                }
            )
        best_review = _best(scored_reviews)
        local_scores = local_quality.get(paper_id, {}).get("scores", {})
        local_paper_only = local_scores.get("baseline", {}).get("overall")
        local_review_guided = local_scores.get("review_guided", {}).get("overall")
        local_delta = None
        if isinstance(local_paper_only, (int, float)) and isinstance(local_review_guided, (int, float)):
            local_delta = local_review_guided - local_paper_only
        best_score = best_review["frontier_signal"]["score"] if best_review else 0.0
        review_beats_paper = best_score > paper_signal["score"]
        review_beats_artifact = best_score > artifact_signal["score"]
        latent_delayed = bool(
            best_review
            and local_delta is not None
            and local_delta <= 0
            and review_beats_paper
            and best_review["frontier_signal"]["frontier_alignment"] > 0
        )
        if not terms:
            pattern = "not_scored_no_frontier_terms"
        elif latent_delayed:
            pattern = "latent_delayed_value_candidate"
        elif review_beats_paper and review_beats_artifact:
            pattern = "review_contains_unrealized_frontier_signal"
        elif review_beats_paper:
            pattern = "review_beats_paper_context"
        else:
            pattern = "paper_or_artifact_already_contains_signal"
        per_paper.append(
            {
                "paper_id": paper_id,
                "title": paper["title"],
                "frontier_quality": frontier_row["frontier_quality"],
                "frontier_terms": terms,
                "paper_context_signal": paper_signal,
                "review_guided_artifact_signal": artifact_signal,
                "best_review_snippet": best_review,
                "all_review_snippets": scored_reviews,
                "local_short_term_delta_review_guided_minus_paper_only": local_delta,
                "interpretation": {
                    "review_beats_paper_context": review_beats_paper,
                    "review_beats_review_guided_artifact": review_beats_artifact,
                    "latent_delayed_value_candidate": latent_delayed,
                    "pattern": pattern,
                },
            }
        )

    usable = [item for item in per_paper if item["frontier_terms"]]
    best_reviews = [item["best_review_snippet"] for item in usable if item["best_review_snippet"]]
    gate_counts = Counter(item["gate"] for item in best_reviews)
    aggregate = {
        "paper_count": len(per_paper),
        "papers_with_frontier_terms": len(usable),
        "review_snippet_count": sum(len(item["all_review_snippets"]) for item in per_paper),
        "review_beats_paper_context_count": sum(
            1 for item in usable if item["interpretation"]["review_beats_paper_context"]
        ),
        "review_beats_review_guided_artifact_count": sum(
            1 for item in usable if item["interpretation"]["review_beats_review_guided_artifact"]
        ),
        "latent_delayed_value_candidate_count": sum(
            1 for item in usable if item["interpretation"]["latent_delayed_value_candidate"]
        ),
        "mean_best_review_score": round(mean([item["frontier_signal"]["score"] for item in best_reviews]), 4)
        if best_reviews else 0.0,
        "mean_paper_context_score": round(mean([item["paper_context_signal"]["score"] for item in usable]), 4)
        if usable else 0.0,
        "mean_review_guided_artifact_score": round(
            mean([item["review_guided_artifact_signal"]["score"] for item in usable]), 4
        ) if usable else 0.0,
        "best_review_gate_counts": dict(gate_counts),
    }

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "review_frontier_signal_probe",
        "citation_frontier_source": _rel(citation_path),
        "source_regeneration_summary": _rel(SOURCE_DIR / "summary.json"),
        "per_paper": per_paper,
        "aggregate": aggregate,
        "claim_boundary": (
            "This probe screens historical review snippets for lexical overlap with later "
            "citation-derived frontier terms. It identifies candidate taste/insight signals "
            "that may deserve human-in-the-loop routing, but it does not prove causality, "
            "review quality, or long-term SOTA alignment. The current sample is six papers "
            "and should be treated as design evidence for retrospective mining."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary": _rel(out_dir / "summary.json"), "readme": _rel(out_dir / "README.md")}, indent=2))


if __name__ == "__main__":
    main()
