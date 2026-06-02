#!/usr/bin/env python3
"""Generate and score single-gate OpenReview regeneration artifacts.

This is a small causal-style ablation: each single-gate artifact is regenerated
from the same paper title/abstract plus only the review snippets routed to one
IGRE gate. It is stronger than post-hoc attribution, but still only a small
model-reviewed OpenReview proxy rather than independent human evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
DEFAULT_SOURCE = (
    DOC_DIR
    / "experiments"
    / "openreview_guided_regeneration_probe_20260602_073500"
    / "summary.json"
)
DEFAULT_SCORED_REVIEWS = (
    DOC_DIR
    / "experiments"
    / "review_utility_map_probe_20260602_071500"
    / "scored_reviews.json"
)
DEFAULT_OUT_DIR = DOC_DIR / "experiments" / "single_gate_artifact_ablation_20260602_203000"

TARGET_GATES = [
    "evaluator_stress_test",
    "structured_feedback",
    "scientific_taste_prior",
]
SCORE_DIMENSIONS = [
    "novelty",
    "correctness",
    "clarity",
    "experiment_quality",
    "limitation_honesty",
    "claim_calibration",
    "overall",
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


def _call_monica(
    *,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
) -> dict[str, Any]:
    api_key = os.environ["MONICA_API_KEY"]
    base_url = os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1").rstrip("/")
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
    ).encode("utf-8")
    req = request.Request(
        f"{base_url}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = time.time()
    last_error: str | None = None
    for attempt in range(3):
        try:
            with request.urlopen(req, timeout=300) as resp:  # noqa: S310 - fixed HTTPS API endpoint.
                payload = json.loads(resp.read().decode("utf-8"))
            payload["_latency_seconds"] = round(time.time() - started, 3)
            payload["_attempts"] = attempt + 1
            return payload
        except (HTTPError, URLError) as exc:
            last_error = repr(exc)
            time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"Monica request failed after retries: {last_error}")


def _message_text(response: dict[str, Any]) -> str:
    return response["choices"][0]["message"]["content"]


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.S)
    if fenced:
        return json.loads(fenced.group(1))
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("model response does not contain a JSON object")
    return json.loads(stripped[start : end + 1])


def _short(text: str, limit: int) -> str:
    text = " ".join(str(text).split())
    return text[:limit]


def _selected_index_by_paper(source: dict[str, Any]) -> dict[str, int]:
    return {paper["paper_id"]: int(paper["sample_index"]) for paper in source["selected_papers"]}


def _gate_contexts(source: dict[str, Any], scored_reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    index_by_paper = _selected_index_by_paper(source)
    source_papers = {paper["paper_id"]: paper for paper in source["selected_papers"]}
    contexts: list[dict[str, Any]] = []
    for paper_id, sample_index in index_by_paper.items():
        gate_context: dict[str, list[dict[str, Any]]] = {gate: [] for gate in TARGET_GATES}
        for review in scored_reviews:
            if int(review["paper_index"]) != sample_index:
                continue
            for gate in review.get("primary_gates") or []:
                if gate not in gate_context:
                    continue
                gate_context[gate].append(
                    {
                        "review_id": review["review_id"],
                        "utility_score": review.get("utility_score", 0),
                        "categories": review.get("categories", []),
                        "text_excerpt": _short(review.get("text", ""), 900),
                    }
                )
        paper = source_papers[paper_id]
        contexts.append(
            {
                "paper_id": paper_id,
                "sample_index": sample_index,
                "title": paper["title"],
                "abstract_excerpt": _short(paper.get("abstract_excerpt", ""), 900),
                "available_gates": [gate for gate, rows in gate_context.items() if rows],
                "gate_context": {gate: rows for gate, rows in gate_context.items() if rows},
            }
        )
    return contexts


def _generation_prompt(contexts: list[dict[str, Any]]) -> str:
    compact = []
    for item in contexts:
        compact.append(
            {
                "paper_id": item["paper_id"],
                "title": item["title"],
                "abstract_excerpt": item["abstract_excerpt"],
                "available_gates": item["available_gates"],
                "gate_context": item["gate_context"],
            }
        )
    return f"""
You are running a causal-style single-gate ablation for a human-guided AI
Scientist workflow.

For each paper and each available gate, generate one mini-paper artifact using
ONLY:
- the paper title,
- the paper abstract excerpt,
- the review snippets routed to that specific gate.

Do not use snippets from other gates when generating a single-gate artifact.
The goal is to test what each gate can do on its own.

For every input paper, you MUST generate exactly one artifact for every gate in
that paper's available_gates list. Do not skip structured_feedback or
scientific_taste_prior when they are listed. Do not invent artifacts for gates
that are not listed for that paper.

Available gate meanings:
- evaluator_stress_test: improve evaluation, baselines, metrics, leakage checks,
  correctness checks, and experiment validity.
- structured_feedback: improve clarity, organization, presentation, and concrete
  revision structure.
- scientific_taste_prior: improve problem framing, novelty positioning,
  importance, and choice of high-upside direction.

Each artifact should include:
- gate_used,
- gate_insights_used: 1-3 short bullets,
- core_contribution,
- method_sketch,
- experiment_plan,
- limitations,
- claim_boundary,
- mini_paper_artifact: 150-220 words.

Inputs:
{json.dumps(compact, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "papers": [
    {{
      "paper_id": "...",
      "single_gate_regenerations": {{
        "evaluator_stress_test": {{ "...": "..." }},
        "structured_feedback": {{ "...": "..." }},
        "scientific_taste_prior": {{ "...": "..." }}
      }}
    }}
  ]
}}
""".strip()


def _condition_bundle(source: dict[str, Any], single_gate_generation: dict[str, Any]) -> list[dict[str, Any]]:
    source_by_id = {paper["paper_id"]: paper for paper in source["regenerations"]["papers"]}
    single_by_id = {
        paper["paper_id"]: paper.get("single_gate_regenerations", {})
        for paper in single_gate_generation.get("papers", [])
    }
    bundle = []
    for paper in source["selected_papers"]:
        paper_id = paper["paper_id"]
        existing = source_by_id[paper_id]
        conditions = {
            "baseline": existing["baseline_regeneration"],
            "full_review_guided": existing["review_guided_regeneration"],
        }
        for gate, artifact in single_by_id.get(paper_id, {}).items():
            conditions[f"single_{gate}"] = artifact
        bundle.append(
            {
                "paper_id": paper_id,
                "title": paper["title"],
                "abstract_excerpt": _short(paper.get("abstract_excerpt", ""), 700),
                "conditions": conditions,
            }
        )
    return bundle


def _score_prompt(bundle: list[dict[str, Any]]) -> str:
    return f"""
You are reviewing a single-gate artifact ablation.

For each paper, score each condition listed in that paper's `conditions` object
on 1-5 integer scales:
{', '.join(SCORE_DIMENSIONS)}.

Conditions:
- baseline: generated from title/abstract only.
- full_review_guided: generated from title/abstract plus full paper-specific reviews.
- single_*: generated from title/abstract plus ONLY one gate-specific review signal.

Reward a single-gate artifact only when that isolated gate produces a better
research artifact than baseline. Reward full_review_guided only if combining
review signals improves the artifact without losing focus. It is acceptable for
baseline or a single gate to win.

Important: return scores for exactly the condition keys present for each paper.
Do not add scores for missing single-gate conditions.

Inputs:
{json.dumps(bundle, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "per_paper": [
    {{
      "paper_id": "...",
      "winner": "baseline" | "full_review_guided" | "single_evaluator_stress_test" | "single_structured_feedback" | "single_scientific_taste_prior" | "tie",
      "scores": {{
        "baseline": {{"novelty": 1, "correctness": 1, "clarity": 1, "experiment_quality": 1, "limitation_honesty": 1, "claim_calibration": 1, "overall": 1}},
        "full_review_guided": {{"novelty": 1, "correctness": 1, "clarity": 1, "experiment_quality": 1, "limitation_honesty": 1, "claim_calibration": 1, "overall": 1}},
        "single_evaluator_stress_test": {{"novelty": 1, "correctness": 1, "clarity": 1, "experiment_quality": 1, "limitation_honesty": 1, "claim_calibration": 1, "overall": 1}},
        "single_structured_feedback": {{"novelty": 1, "correctness": 1, "clarity": 1, "experiment_quality": 1, "limitation_honesty": 1, "claim_calibration": 1, "overall": 1}},
        "single_scientific_taste_prior": {{"novelty": 1, "correctness": 1, "clarity": 1, "experiment_quality": 1, "limitation_honesty": 1, "claim_calibration": 1, "overall": 1}}
      }},
      "best_single_gate": "single_evaluator_stress_test" | "single_structured_feedback" | "single_scientific_taste_prior" | "none",
      "useful_gate_signal": "short explanation",
      "failure_or_confound": "short explanation"
    }}
  ],
  "design_lessons": ["lesson 1", "lesson 2", "lesson 3"],
  "claim_boundary": "short paragraph"
}}
""".strip()


def _normalize_review(
    model: str,
    parsed: dict[str, Any],
    allowed_conditions_by_paper: dict[str, set[str]],
) -> dict[str, Any]:
    parsed["model"] = model
    condition_scores: dict[str, list[float]] = defaultdict_list()
    winners: list[str] = []
    best_single_counts: dict[str, int] = {}
    for item in parsed.get("per_paper", []):
        paper_id = item.get("paper_id")
        allowed_conditions = allowed_conditions_by_paper.get(paper_id, set())
        winner = item.get("winner", "tie")
        if winner != "tie" and winner not in allowed_conditions:
            winner = "tie"
            item["winner"] = "tie"
        winners.append(winner)
        best_single = item.get("best_single_gate", "none")
        if best_single != "none" and best_single not in allowed_conditions:
            best_single = "none"
            item["best_single_gate"] = "none"
        best_single_counts[best_single] = best_single_counts.get(best_single, 0) + 1
        for condition, scores in (item.get("scores") or {}).items():
            if condition not in allowed_conditions:
                continue
            overall = scores.get("overall") if isinstance(scores, dict) else None
            if isinstance(overall, (int, float)):
                condition_scores.setdefault(condition, []).append(float(overall))
    parsed["aggregate"] = {
        "winner_counts": {winner: winners.count(winner) for winner in sorted(set(winners))},
        "best_single_gate_counts": best_single_counts,
        "mean_overall_by_condition": {
            condition: round(sum(values) / len(values), 4)
            for condition, values in sorted(condition_scores.items())
            if values
        },
    }
    return parsed


def defaultdict_list() -> dict[str, list[float]]:
    return {}


def _aggregate_reviews(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    condition_values: dict[str, list[float]] = {}
    winner_counts: dict[str, int] = {}
    best_single_counts: dict[str, int] = {}
    per_paper_votes: dict[str, dict[str, int]] = {}
    for review in reviews:
        agg = review["aggregate"]
        for condition, value in agg["mean_overall_by_condition"].items():
            condition_values.setdefault(condition, []).append(float(value))
        for winner, count in agg["winner_counts"].items():
            winner_counts[winner] = winner_counts.get(winner, 0) + int(count)
        for gate, count in agg["best_single_gate_counts"].items():
            best_single_counts[gate] = best_single_counts.get(gate, 0) + int(count)
        for item in review.get("per_paper", []):
            votes = per_paper_votes.setdefault(item["paper_id"], {})
            winner = item.get("winner", "tie")
            votes[winner] = votes.get(winner, 0) + 1
    mean_overall = {
        condition: round(sum(values) / len(values), 4)
        for condition, values in sorted(condition_values.items())
        if values
    }
    single_conditions = {
        key: value
        for key, value in mean_overall.items()
        if key.startswith("single_")
    }
    best_single_condition = max(single_conditions, key=single_conditions.get) if single_conditions else "none"
    return {
        "model_count": len(reviews),
        "winner_counts": winner_counts,
        "best_single_gate_counts": best_single_counts,
        "mean_overall_by_condition": mean_overall,
        "best_single_condition_by_mean": best_single_condition,
        "full_review_guided_minus_baseline": round(
            mean_overall.get("full_review_guided", 0.0) - mean_overall.get("baseline", 0.0),
            4,
        ),
        "full_review_guided_minus_best_single": round(
            mean_overall.get("full_review_guided", 0.0) - mean_overall.get(best_single_condition, 0.0),
            4,
        ),
        "best_single_minus_baseline": round(
            mean_overall.get(best_single_condition, 0.0) - mean_overall.get("baseline", 0.0),
            4,
        ),
        "per_paper_votes": per_paper_votes,
    }


def _markdown(summary: dict[str, Any]) -> str:
    agg = summary["aggregate"]
    lines = [
        "# Single-Gate Artifact Ablation",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Generation model: `{summary['generation_model']}`",
        f"- Reviewer models: `{', '.join(summary['review_models'])}`",
        f"- Papers: `{summary['paper_count']}`",
        f"- Live model calls: `{summary['live_model_calls']}`",
        "",
        "## Mean Overall By Condition",
        "",
        "| Condition | Mean overall |",
        "| --- | ---: |",
    ]
    for condition, value in agg["mean_overall_by_condition"].items():
        lines.append(f"| `{condition}` | {value:.4f} |")
    lines.extend(
        [
            "",
            "## Aggregate",
            "",
            f"- Winner counts: `{json.dumps(agg['winner_counts'], sort_keys=True)}`",
            f"- Best single gate counts: `{json.dumps(agg['best_single_gate_counts'], sort_keys=True)}`",
            f"- Best single condition by mean: `{agg['best_single_condition_by_mean']}`",
            f"- Full review-guided minus baseline: `{agg['full_review_guided_minus_baseline']}`",
            f"- Full review-guided minus best single: `{agg['full_review_guided_minus_best_single']}`",
            f"- Best single minus baseline: `{agg['best_single_minus_baseline']}`",
            "",
            "## Interpretation",
            "",
            summary["interpretation"],
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    source = _load_json(args.source)
    scored_reviews = _load_json(args.scored_reviews)
    contexts = _gate_contexts(source, scored_reviews)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    generation_prompt = _generation_prompt(contexts)
    _write(out_dir / "generation_prompt.txt", generation_prompt)
    generation_response = _call_monica(
        model=args.generation_model,
        messages=[
            {"role": "system", "content": "Return strict JSON only."},
            {"role": "user", "content": generation_prompt},
        ],
        max_tokens=args.generation_max_tokens,
        temperature=0.2,
    )
    generation_text = _message_text(generation_response)
    _write(out_dir / "generation_raw_response.txt", generation_text)
    generation = _extract_json_object(generation_text)
    generated_path = _write(
        out_dir / "single_gate_artifacts.json",
        json.dumps(generation, indent=2, ensure_ascii=False),
    )

    expected_gates_by_paper = {
        item["paper_id"]: set(item["available_gates"])
        for item in contexts
    }
    generated_gates_by_paper = {
        paper.get("paper_id"): set((paper.get("single_gate_regenerations") or {}).keys())
        for paper in generation.get("papers", [])
    }
    missing_generated_gates = {
        paper_id: sorted(expected - generated_gates_by_paper.get(paper_id, set()))
        for paper_id, expected in expected_gates_by_paper.items()
        if expected - generated_gates_by_paper.get(paper_id, set())
    }

    bundle = _condition_bundle(source, generation)
    allowed_conditions_by_paper = {
        item["paper_id"]: set(item["conditions"])
        for item in bundle
    }
    scoring_prompt = _score_prompt(bundle)
    _write(out_dir / "scoring_prompt.txt", scoring_prompt)
    reviews: list[dict[str, Any]] = []
    raw_paths = []
    for model in args.review_models:
        max_tokens = args.review_max_tokens_claude if "claude" in model else args.review_max_tokens
        response = _call_monica(
            model=model,
            messages=[
                {"role": "system", "content": "Return strict JSON only."},
                {"role": "user", "content": scoring_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.0,
        )
        text = _message_text(response)
        raw_paths.append(_write(out_dir / f"{model}_raw_response.txt", text))
        parsed = _normalize_review(model, _extract_json_object(text), allowed_conditions_by_paper)
        review_path = _write(out_dir / f"{model}_review.json", json.dumps(parsed, indent=2, ensure_ascii=False))
        parsed["_review_path"] = review_path
        parsed["_latency_seconds"] = response.get("_latency_seconds")
        reviews.append(parsed)

    aggregate = _aggregate_reviews(reviews)
    status = (
        "pass"
        if not missing_generated_gates
        and aggregate["best_single_minus_baseline"] >= 0
        and aggregate["full_review_guided_minus_baseline"] >= 0
        else "attention"
    )
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": status,
        "source_summary": _rel(args.source),
        "source_scored_reviews": _rel(args.scored_reviews),
        "generation_model": args.generation_model,
        "review_models": args.review_models,
        "paper_count": len(contexts),
        "target_gates": TARGET_GATES,
        "live_model_calls": 1 + len(args.review_models),
        "gate_contexts": contexts,
        "missing_generated_gates": missing_generated_gates,
        "single_gate_artifacts": generated_path,
        "reviews": reviews,
        "aggregate": aggregate,
        "interpretation": (
            "This single-gate artifact ablation generates new artifacts using only "
            "one gate-specific review signal. It therefore moves beyond post-hoc "
            "attribution. The result should be read as a small OpenReview proxy for "
            "which gates are useful in isolation and whether full review guidance "
            "still adds value over isolated gates."
        ),
        "claim_boundary": (
            "This is a six-paper, model-reviewed OpenReview proxy using generated "
            "mini-paper artifacts. It is closer to a causal gate ablation than "
            "post-hoc attribution, but it does not replace independent human expert "
            "ratings, real benchmark reruns, or multi-task AI Scientist-v2 matched "
            "experiments."
        ),
    }
    summary["summary_path"] = _write(out_dir / "summary.json", json.dumps(summary, indent=2, ensure_ascii=False))
    summary["readme_path"] = _write(out_dir / "README.md", _markdown(summary))
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="single_gate_artifact_ablation_20260602_203000")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--scored-reviews", type=Path, default=DEFAULT_SCORED_REVIEWS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--generation-model", default="gpt-4o-mini")
    parser.add_argument("--review-models", nargs="+", default=["gpt-4o-mini", "claude-3-7-sonnet-latest"])
    parser.add_argument("--generation-max-tokens", type=int, default=9000)
    parser.add_argument("--review-max-tokens", type=int, default=7000)
    parser.add_argument("--review-max-tokens-claude", type=int, default=4200)
    return parser.parse_args()


def main() -> None:
    summary = run(parse_args())
    print(json.dumps({"summary": summary["summary_path"], "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
