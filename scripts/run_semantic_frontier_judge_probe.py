#!/usr/bin/env python3
"""Model-judged semantic future-frontier alignment probe.

Lexical overlap is a weak proxy for whether a review comment would have moved a
research workflow toward later field directions. This probe asks a small
Monica-routed judge to compare paper context, review-guided artifacts, and the
best historical review snippet against citation-derived future-frontier
metadata.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SOURCE_DIR = DOC_DIR / "experiments" / "openreview_guided_regeneration_probe_20260602_073500"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _truncate(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " ..."


def _artifact_text(artifact: dict[str, Any]) -> str:
    parts = []
    for key in [
        "core_contribution",
        "method_sketch",
        "experiment_plan",
        "limitations",
        "claim_boundary",
        "mini_paper_artifact",
    ]:
        value = artifact.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    return "\n".join(parts)


def _call_model(model: str, prompt: str, max_tokens: int) -> dict[str, Any]:
    base_url = os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1").rstrip("/")
    api_key = os.environ["MONICA_API_KEY"]
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You judge scientific research-direction alignment. "
                        "Return strict JSON only. Do not add Markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "max_tokens": max_tokens,
        },
        timeout=180,
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {"error": "non_json_response", "text_excerpt": response.text[:2000]}
    return {"model": model, "status_code": response.status_code, "response": payload}


def _extract_content(result: dict[str, Any]) -> str:
    choices = result.get("response", {}).get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return message.get("content") or ""


def _parse_json_text(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _prompt(row: dict[str, Any], record: dict[str, Any], candidates: dict[str, str]) -> str:
    citations = []
    for citation in (record.get("citations_used") or [])[:8]:
        citations.append(
            {
                "title": citation.get("title"),
                "year": citation.get("year"),
                "abstract_excerpt": _truncate(citation.get("abstract") or "", 500),
            }
        )
    candidate_view = {
        key: _truncate(value, 1100)
        for key, value in candidates.items()
    }
    return f"""We are evaluating historical peer-review signals for automated science.

Original paper:
{{
  "paper_id": {json.dumps(row["paper_id"])},
  "title": {json.dumps(row["title"])},
  "frontier_terms": {json.dumps(row.get("frontier_terms") or [])}
}}

Later citing-paper frontier metadata:
{json.dumps(citations, ensure_ascii=False, indent=2)}

Candidate signals available at the historical time:
{json.dumps(candidate_view, ensure_ascii=False, indent=2)}

Score each candidate from 1 to 5:
- semantic_frontier_alignment: would it steer an automated researcher toward the later citing-paper frontier?
- actionable_research_control: does it imply a concrete experiment, evaluator, method change, or claim boundary?
- novelty_taste_signal: does it express non-generic scientific taste about what is worth pursuing?

Then choose winner among: paper_context, review_guided_artifact, best_review_snippet.
Also set latent_delayed_value_candidate=true only if the best_review_snippet is the winner and the reason says it could steer future research even if immediate artifact quality is not better.

Return JSON only with this schema:
{{
  "scores": {{
    "paper_context": {{"semantic_frontier_alignment": 1, "actionable_research_control": 1, "novelty_taste_signal": 1}},
    "review_guided_artifact": {{"semantic_frontier_alignment": 1, "actionable_research_control": 1, "novelty_taste_signal": 1}},
    "best_review_snippet": {{"semantic_frontier_alignment": 1, "actionable_research_control": 1, "novelty_taste_signal": 1}}
  }},
  "winner": "paper_context",
  "latent_delayed_value_candidate": false,
  "reason": "one concise sentence"
}}
"""


def _summarize(per_paper: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [item for item in per_paper if item.get("status") == "success"]
    winner_counts = Counter(item["judgement"]["winner"] for item in successful)
    latent = sum(1 for item in successful if item["derived_temporal_pattern"] == "semantic_delayed_value_candidate")
    frontier_steering = sum(
        1 for item in successful
        if item["derived_temporal_pattern"] == "semantic_frontier_steering_candidate"
    )
    means: dict[str, dict[str, float]] = {}
    for candidate in ["paper_context", "review_guided_artifact", "best_review_snippet"]:
        means[candidate] = {}
        for metric in ["semantic_frontier_alignment", "actionable_research_control", "novelty_taste_signal"]:
            values = [
                item["judgement"]["scores"][candidate][metric]
                for item in successful
                if candidate in item["judgement"].get("scores", {})
            ]
            means[candidate][metric] = round(mean(values), 4) if values else 0.0
    return {
        "paper_count": len(per_paper),
        "successful_judgements": len(successful),
        "failed_judgements": len(per_paper) - len(successful),
        "winner_counts": dict(winner_counts),
        "latent_delayed_value_candidate_count": latent,
        "semantic_frontier_steering_candidate_count": frontier_steering,
        "mean_scores": means,
    }


def _markdown(summary: dict[str, Any]) -> str:
    aggregate = summary["aggregate"]
    lines = [
        "# Semantic Frontier Judge Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Judge model: `{summary['judge_model']}`",
        "",
        "## Aggregate",
        "",
        f"- Successful judgements: `{aggregate['successful_judgements']}` / `{aggregate['paper_count']}`",
        f"- Winner counts: `{json.dumps(aggregate['winner_counts'], sort_keys=True)}`",
        f"- Latent delayed-value candidates: `{aggregate['latent_delayed_value_candidate_count']}`",
        f"- Semantic frontier-steering candidates: `{aggregate['semantic_frontier_steering_candidate_count']}`",
        f"- Mean scores: `{json.dumps(aggregate['mean_scores'], sort_keys=True)}`",
        "",
        "## Per Paper",
        "",
    ]
    for item in summary["per_paper"]:
        if item.get("status") != "success":
            lines.append(f"- `{item['paper_id']}`: failed judgement `{item.get('error')}`")
            continue
        judgement = item["judgement"]
        lines.append(
            f"- `{item['paper_id']}`: winner `{judgement['winner']}`; "
            f"pattern `{item['derived_temporal_pattern']}`; "
            f"reason: {judgement.get('reason')}"
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--citation-summary", required=True)
    parser.add_argument("--review-signal-summary", required=True)
    parser.add_argument("--run-id", default="semantic_frontier_judge_probe_20260602_221500")
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--max-papers", type=int, default=None)
    parser.add_argument("--max-tokens", type=int, default=1200)
    args = parser.parse_args()

    citation_path = Path(args.citation_summary)
    if not citation_path.is_absolute():
        citation_path = ROOT / citation_path
    review_signal_path = Path(args.review_signal_summary)
    if not review_signal_path.is_absolute():
        review_signal_path = ROOT / review_signal_path

    citation_summary = _load_json(citation_path)
    retrieval = {
        row["paper_id"]: row
        for row in _load_json(citation_path.parent / "retrieval_records.json")
    }
    review_signal = {
        row["paper_id"]: row
        for row in _load_json(review_signal_path)["per_paper"]
    }
    selected = {item["paper_id"]: item for item in _load_json(SOURCE_DIR / "selected_papers.json")}
    regenerated = {
        item["paper_id"]: item
        for item in _load_json(SOURCE_DIR / "regenerated_artifacts.json")["papers"]
    }

    rows = [row for row in citation_summary["per_paper"] if row.get("frontier_terms")]
    if args.max_papers is not None:
        rows = rows[: args.max_papers]

    per_paper = []
    raw_calls = []
    for row in rows:
        paper_id = row["paper_id"]
        paper = selected[paper_id]
        best_review = review_signal[paper_id].get("best_review_snippet") or {}
        candidates = {
            "paper_context": "\n".join(
                [
                    paper.get("title") or "",
                    paper.get("abstract_excerpt") or "",
                    paper.get("decision_text_excerpt") or "",
                ]
            ),
            "review_guided_artifact": _artifact_text(regenerated[paper_id]["review_guided_regeneration"]),
            "best_review_snippet": best_review.get("excerpt") or "",
        }
        prompt = _prompt(row, retrieval.get(paper_id, {}), candidates)
        result = _call_model(args.model, prompt, args.max_tokens)
        content = _extract_content(result)
        raw_calls.append({"paper_id": paper_id, "prompt": prompt, "result": result, "content": content})
        if result["status_code"] != 200:
            per_paper.append(
                {
                    "paper_id": paper_id,
                    "title": row["title"],
                    "status": "failed",
                    "status_code": result["status_code"],
                    "error": "non_200_model_response",
                }
            )
            continue
        try:
            judgement = _parse_json_text(content)
            winner = judgement.get("winner")
            local_delta = review_signal[paper_id].get("local_short_term_delta_review_guided_minus_paper_only")
            human_guided_winner = winner in {"review_guided_artifact", "best_review_snippet"}
            if human_guided_winner and isinstance(local_delta, (int, float)) and local_delta < 0:
                derived_temporal_pattern = "semantic_delayed_value_candidate"
            elif human_guided_winner and isinstance(local_delta, (int, float)) and local_delta <= 0:
                derived_temporal_pattern = "semantic_frontier_steering_candidate"
            elif human_guided_winner:
                derived_temporal_pattern = "short_and_semantic_positive"
            else:
                derived_temporal_pattern = "paper_context_remains_stronger"
            judgement["latent_delayed_value_candidate"] = (
                derived_temporal_pattern == "semantic_delayed_value_candidate"
            )
            per_paper.append(
                {
                    "paper_id": paper_id,
                    "title": row["title"],
                    "frontier_quality": row["frontier_quality"],
                    "citation_count_used": row["citation_count_used"],
                    "status": "success",
                    "judgement": judgement,
                    "local_short_term_delta_review_guided_minus_paper_only": local_delta,
                    "derived_temporal_pattern": derived_temporal_pattern,
                }
            )
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            per_paper.append(
                {
                    "paper_id": paper_id,
                    "title": row["title"],
                    "status": "failed",
                    "error": f"parse_error: {exc}",
                    "content_excerpt": content[:1000],
                }
            )

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "semantic_frontier_judge_probe",
        "judge_model": args.model,
        "citation_frontier_source": _rel(citation_path),
        "review_signal_source": _rel(review_signal_path),
        "per_paper": per_paper,
        "aggregate": _summarize(per_paper),
        "claim_boundary": (
            "This is a small model-judged semantic probe over citation-derived frontier "
            "metadata. It addresses the lexical-overlap limitation but remains model-routed "
            "and non-causal; it should be treated as a prioritization signal for future "
            "human expert review, not as proof of delayed-value scientific taste."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")
    (out_dir / "raw_model_calls.json").write_text(json.dumps(raw_calls, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": _rel(out_dir / "summary.json"), "readme": _rel(out_dir / "README.md")}, indent=2))


if __name__ == "__main__":
    main()
