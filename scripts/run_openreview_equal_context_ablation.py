#!/usr/bin/env python3
"""Run an equal-context ablation for OpenReview-guided regeneration.

The earlier regeneration probe compared title/abstract-only artifacts with
artifacts that also saw real review text. This script addresses the obvious
confound: the review-guided condition had more context. It creates a
matched-length context-control condition using unrelated OpenReview snippets,
then asks one or more reviewer models whether real, paper-specific reviews
still improve the generated artifact.
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
EXPERT_PROBE_DIR = DOC_DIR / "experiments" / "expert_review_taste_prior_probe_20260602_031800"
DEFAULT_SOURCE = (
    DOC_DIR
    / "experiments"
    / "openreview_guided_regeneration_probe_20260602_073500"
    / "summary.json"
)


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
            with request.urlopen(req, timeout=240) as resp:  # noqa: S310 - fixed HTTPS API endpoint.
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


def _target_review_text(paper: dict[str, Any]) -> str:
    parts = []
    if paper.get("decision_text_excerpt"):
        parts.append(str(paper["decision_text_excerpt"]))
    parts.extend(str(snippet) for snippet in paper.get("review_snippets", [])[:3])
    return "\n\n".join(parts)


def _matched_unrelated_context(
    *,
    rows: list[dict[str, Any]],
    source_indices: list[int],
    target_index: int,
    target_length: int,
) -> str:
    """Build unrelated review context with approximately the target length."""

    pieces: list[str] = []
    for offset in range(1, len(rows)):
        candidate_index = (target_index + offset) % len(rows)
        if candidate_index in source_indices:
            continue
        row = rows[candidate_index]
        snippets = row.get("review_snippets") or []
        if not snippets:
            continue
        for snippet in snippets:
            if snippet:
                pieces.append(
                    f"[Unrelated OpenReview snippet from sample {candidate_index}, "
                    f"title: {row.get('title')}]\n{snippet}"
                )
            if sum(len(piece) for piece in pieces) >= target_length:
                break
        if sum(len(piece) for piece in pieces) >= target_length:
            break
    context = "\n\n".join(pieces)
    return context[:target_length]


def _compact_source(source: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    papers = source["selected_papers"]
    by_id = {paper["paper_id"]: paper for paper in source["regenerations"]["papers"]}
    return papers, by_id


def _make_control_inputs(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _load_json(EXPERT_PROBE_DIR / "sample_rows_compact.json")
    selected, guided_by_id = _compact_source(source)
    selected_indices = [int(paper["sample_index"]) for paper in selected]
    controls = []
    for paper in selected:
        target_text = _target_review_text(paper)
        unrelated = _matched_unrelated_context(
            rows=rows,
            source_indices=selected_indices,
            target_index=int(paper["sample_index"]),
            target_length=max(800, min(len(target_text), 2600)),
        )
        guided = guided_by_id[paper["paper_id"]]["review_guided_regeneration"]
        controls.append(
            {
                "paper_id": paper["paper_id"],
                "title": paper.get("title"),
                "abstract_excerpt": paper.get("abstract_excerpt"),
                "mean_score": paper.get("mean_score"),
                "decision": paper.get("decision"),
                "matched_context_length": len(unrelated),
                "real_review_context_length": len(target_text),
                "unrelated_context": unrelated,
                "review_guided_artifact": guided,
            }
        )
    return controls


def _generation_prompt(controls: list[dict[str, Any]]) -> str:
    compact = [
        {
            "paper_id": item["paper_id"],
            "title": item["title"],
            "abstract_excerpt": item["abstract_excerpt"],
            "matched_context_length": item["matched_context_length"],
            "unrelated_context": item["unrelated_context"],
        }
        for item in controls
    ]
    return f"""
You are running an equal-context ablation for review-guided research artifact generation.

For each paper, generate one context_control_regeneration artifact. You may use:
- the paper title,
- the paper abstract excerpt,
- the matched-length unrelated OpenReview snippets.

Important: the unrelated snippets are NOT reviews of the target paper. Do not
treat their factual criticisms as facts about the target. Use them only as
generic reviewer-style pressure to improve problem framing, experiment design,
limitation honesty, and claim calibration. This control tests whether real
paper-specific reviews are more useful than equal amounts of generic review
context.

Each artifact should include:
- core_contribution,
- method_sketch,
- experiment_plan,
- limitations,
- claim_boundary,
- mini_paper_artifact of 220-320 words.

Inputs:
{json.dumps(compact, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "papers": [
    {{
      "paper_id": "...",
      "context_control_regeneration": {{
        "generic_review_pressures_used": ["..."],
        "core_contribution": "...",
        "method_sketch": "...",
        "experiment_plan": "...",
        "limitations": "...",
        "claim_boundary": "...",
        "mini_paper_artifact": "220-320 words"
      }}
    }}
  ]
}}
""".strip()


def _score_prompt(controls: list[dict[str, Any]], control_generation: dict[str, Any]) -> str:
    generated_by_id = {
        item["paper_id"]: item["context_control_regeneration"]
        for item in control_generation.get("papers", [])
    }
    pairs = []
    for item in controls:
        pairs.append(
            {
                "paper_id": item["paper_id"],
                "title": item["title"],
                "abstract_excerpt": item["abstract_excerpt"],
                "context_control": generated_by_id.get(item["paper_id"], {}),
                "review_guided": item["review_guided_artifact"],
            }
        )
    return f"""
You are independently reviewing an equal-context ablation.

For each paper, compare:
- context_control: generated from title/abstract plus matched-length unrelated
  OpenReview snippets. It saw extra reviewer-style text but not real reviews of
  the target paper.
- review_guided: generated from title/abstract plus real paper-specific
  OpenReview reviews and decision text.

Reward review_guided only if the paper-specific review insight improves
problem framing, method design, experiment planning, limitation honesty, or
claim calibration beyond generic reviewer pressure. It is acceptable for the
context control to win.

Pairs:
{json.dumps(pairs, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "per_paper": [
    {{
      "paper_id": "...",
      "winner": "context_control" | "review_guided" | "tie",
      "scores": {{
        "context_control": {{
          "novelty": 1-5,
          "correctness": 1-5,
          "clarity": 1-5,
          "experiment_quality": 1-5,
          "limitation_honesty": 1-5,
          "claim_calibration": 1-5,
          "overall": 1-5
        }},
        "review_guided": {{
          "novelty": 1-5,
          "correctness": 1-5,
          "clarity": 1-5,
          "experiment_quality": 1-5,
          "limitation_honesty": 1-5,
          "claim_calibration": 1-5,
          "overall": 1-5
        }}
      }},
      "specific_review_value": "short explanation",
      "remaining_confounds": "short explanation"
    }}
  ],
  "design_lessons": ["lesson 1", "lesson 2", "lesson 3"],
  "claim_boundary": "short paragraph"
}}
""".strip()


def _normalize_review(model: str, parsed: dict[str, Any]) -> dict[str, Any]:
    per_paper = parsed.get("per_paper") or []
    control_scores = []
    guided_scores = []
    winners = []
    for item in per_paper:
        winners.append(item.get("winner"))
        scores = item.get("scores") or {}
        control = scores.get("context_control") or {}
        guided = scores.get("review_guided") or {}
        if isinstance(control.get("overall"), (int, float)):
            control_scores.append(float(control["overall"]))
        if isinstance(guided.get("overall"), (int, float)):
            guided_scores.append(float(guided["overall"]))
    mean_control = sum(control_scores) / len(control_scores) if control_scores else 0.0
    mean_guided = sum(guided_scores) / len(guided_scores) if guided_scores else 0.0
    parsed["model"] = model
    parsed["aggregate"] = {
        "review_guided_wins": sum(1 for winner in winners if winner == "review_guided"),
        "context_control_wins": sum(1 for winner in winners if winner == "context_control"),
        "ties": sum(1 for winner in winners if winner == "tie"),
        "mean_context_control_overall": round(mean_control, 4),
        "mean_review_guided_overall": round(mean_guided, 4),
        "mean_delta_review_guided_minus_context_control": round(mean_guided - mean_control, 4),
    }
    return parsed


def _aggregate_reviews(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "model_count": len(reviews),
        "review_guided_wins": 0,
        "context_control_wins": 0,
        "ties": 0,
        "mean_delta_by_model": [],
        "per_paper_votes": {},
    }
    for review in reviews:
        agg = review.get("aggregate", {})
        totals["review_guided_wins"] += int(agg.get("review_guided_wins", 0))
        totals["context_control_wins"] += int(agg.get("context_control_wins", 0))
        totals["ties"] += int(agg.get("ties", 0))
        totals["mean_delta_by_model"].append(agg.get("mean_delta_review_guided_minus_context_control"))
        for item in review.get("per_paper", []):
            votes = totals["per_paper_votes"].setdefault(
                item.get("paper_id", "unknown"),
                {"review_guided": 0, "context_control": 0, "tie": 0},
            )
            winner = item.get("winner")
            if winner in votes:
                votes[winner] += 1
    numeric = [value for value in totals["mean_delta_by_model"] if isinstance(value, (int, float))]
    totals["mean_delta_across_models"] = round(sum(numeric) / len(numeric), 4) if numeric else 0.0
    return totals


def _markdown(summary: dict[str, Any]) -> str:
    agg = summary["aggregate"]
    lines = [
        "# OpenReview Equal-Context Ablation",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Source run: `{summary['source_run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Generation model: `{summary['generation_model']}`",
        f"- Reviewer models: `{', '.join(summary['review_models'])}`",
        f"- Pair count: `{summary['pair_count']}`",
        f"- Review-guided wins: `{agg['review_guided_wins']}`",
        f"- Context-control wins: `{agg['context_control_wins']}`",
        f"- Ties: `{agg['ties']}`",
        f"- Mean delta across models: `{agg['mean_delta_across_models']}`",
        "",
        "## Design",
        "",
        "The earlier OpenReview regeneration probe compared title/abstract-only",
        "artifacts against title/abstract plus real review text. This ablation",
        "controls for extra context by generating a matched-length",
        "`context_control` artifact from unrelated OpenReview snippets. The",
        "reviewers then compare that control with the existing paper-specific",
        "`review_guided` artifact.",
        "",
        "## Model Results",
        "",
        "| Model | Review-guided wins | Context-control wins | Ties | Mean delta |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for review in summary["reviews"]:
        model_agg = review["aggregate"]
        lines.append(
            f"| `{review['model']}` | {model_agg['review_guided_wins']} | "
            f"{model_agg['context_control_wins']} | {model_agg['ties']} | "
            f"{model_agg['mean_delta_review_guided_minus_context_control']} |"
        )
    lines.extend(["", "## Pairwise Votes", ""])
    for paper_id, votes in agg["per_paper_votes"].items():
        lines.append(
            f"- `{paper_id}`: review_guided={votes['review_guided']}, "
            f"context_control={votes['context_control']}, tie={votes['tie']}"
        )
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_openreview_equal_context_ablation"
    manifest["openreview_equal_context_ablation"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "source_run_id": summary["source_run_id"],
        "pair_count": summary["pair_count"],
        "review_models": summary["review_models"],
        "review_guided_wins": summary["aggregate"]["review_guided_wins"],
        "context_control_wins": summary["aggregate"]["context_control_wins"],
        "ties": summary["aggregate"]["ties"],
        "mean_delta_across_models": summary["aggregate"]["mean_delta_across_models"],
        "claim_boundary": summary["claim_boundary"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-summary", default=str(DEFAULT_SOURCE.relative_to(ROOT)))
    parser.add_argument("--run-id", default=f"openreview_equal_context_ablation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--generation-model", default="gpt-4o-mini")
    parser.add_argument(
        "--review-models",
        nargs="+",
        default=["gpt-4o-mini", "claude-3-7-sonnet-latest"],
    )
    parser.add_argument("--generation-max-tokens", type=int, default=6000)
    parser.add_argument("--review-max-tokens", type=int, default=4000)
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    source = _load_json(ROOT / args.source_summary)
    controls = _make_control_inputs(source)
    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    generation_prompt = _generation_prompt(controls)
    generation_response = _call_monica(
        model=args.generation_model,
        messages=[
            {"role": "system", "content": "Return strict JSON. Keep all claims evidence-bound."},
            {"role": "user", "content": generation_prompt},
        ],
        max_tokens=args.generation_max_tokens,
        temperature=0.35,
    )
    generation_text = _message_text(generation_response)
    control_generation = _extract_json_object(generation_text)

    score_prompt = _score_prompt(controls, control_generation)
    reviews = []
    paths = [
        _write(out_dir / "source_summary_path.txt", args.source_summary),
        _write(out_dir / "control_inputs.json", json.dumps(controls, ensure_ascii=False, indent=2)),
        _write(out_dir / "generation_prompt.txt", generation_prompt),
        _write(out_dir / "generation_raw_response.txt", generation_text),
        _write(out_dir / "context_control_artifacts.json", json.dumps(control_generation, ensure_ascii=False, indent=2)),
        _write(out_dir / "review_prompt.txt", score_prompt),
    ]
    for model in args.review_models:
        response = _call_monica(
            model=model,
            messages=[
                {"role": "system", "content": "Return strict JSON. Score conservatively."},
                {"role": "user", "content": score_prompt},
            ],
            max_tokens=args.review_max_tokens,
            temperature=0.1,
        )
        raw_text = _message_text(response)
        parsed = _normalize_review(model, _extract_json_object(raw_text))
        safe_name = model.replace("/", "_").replace(":", "_")
        paths.append(_write(out_dir / f"{safe_name}_raw_response.txt", raw_text))
        paths.append(_write(out_dir / f"{safe_name}_review.json", json.dumps(parsed, ensure_ascii=False, indent=2)))
        reviews.append(parsed)

    aggregate = _aggregate_reviews(reviews)
    summary: dict[str, Any] = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "openreview_equal_context_ablation",
        "source_run_id": source["run_id"],
        "source_summary": args.source_summary,
        "generation_model": args.generation_model,
        "review_models": args.review_models,
        "live_model_calls": 1 + len(args.review_models),
        "pair_count": len(controls),
        "generation_latency_seconds": generation_response.get("_latency_seconds"),
        "reviews": reviews,
        "aggregate": aggregate,
        "claim_boundary": (
            "This ablation controls for extra context by comparing real paper-specific "
            "review guidance against matched-length unrelated review context. It still "
            "uses model-routed scoring rather than independent human expert review, and "
            "does not rerun the original experiments."
        ),
    }
    summary_path = out_dir / "summary.json"
    summary["summary_path"] = _rel(summary_path)
    paths.extend(
        [
            _write(summary_path, json.dumps(summary, ensure_ascii=False, indent=2)),
            _write(out_dir / "README.md", _markdown(summary)),
        ]
    )
    summary["artifacts_written"] = paths
    _write(summary_path, json.dumps(summary, ensure_ascii=False, indent=2))
    _update_manifest(paths + ["scripts/run_openreview_equal_context_ablation.py"], summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
