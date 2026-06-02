#!/usr/bin/env python3
"""Cross-model review for OpenReview-guided regeneration artifacts.

The generation probe creates baseline and review-guided mini-paper artifacts.
This script reuses those artifacts and asks independent Monica-routed models to
score the same A/B pairs, reducing same-model generation/scoring bias.
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


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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
            with request.urlopen(req, timeout=180) as resp:  # noqa: S310 - fixed HTTPS endpoint.
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


def _compact_source(source: dict[str, Any]) -> dict[str, Any]:
    papers_by_id = {paper["paper_id"]: paper for paper in source["selected_papers"]}
    regen_by_id = {paper["paper_id"]: paper for paper in source["regenerations"]["papers"]}
    pairs = []
    for paper_id, paper in regen_by_id.items():
        meta = papers_by_id[paper_id]
        pairs.append(
            {
                "paper_id": paper_id,
                "title": meta.get("title"),
                "decision": meta.get("decision"),
                "mean_score": meta.get("mean_score"),
                "review_snippets_excerpt": [snippet[:450] for snippet in meta.get("review_snippets", [])[:2]],
                "baseline": paper.get("baseline_regeneration", {}),
                "review_guided": paper.get("review_guided_regeneration", {}),
            }
        )
    return {
        "source_run_id": source["run_id"],
        "source_summary": source["summary_path"],
        "pairs": pairs,
    }


def _review_prompt(compact: dict[str, Any]) -> str:
    return f"""
You are independently reviewing generated mini-paper artifacts. You did not
generate them.

For each OpenReview paper, compare:
- baseline: generated from title/abstract only.
- review_guided: generated from title/abstract plus real review snippets and
  decision text, used as human scientific taste/insight.

Score only the generated artifacts. Do not reward the review-guided artifact
merely because it saw more text; reward it only if it produces better problem
framing, method design, experiment planning, limitation honesty, or claim
calibration. It is acceptable for baseline to win.

Pairs:
{json.dumps(compact, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "per_paper": [
    {{
      "paper_id": "...",
      "winner": "baseline" | "review_guided" | "tie",
      "scores": {{
        "baseline": {{
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
      "rationale": "short explanation",
      "risk": "short remaining risk"
    }}
  ],
  "design_lessons": ["lesson 1", "lesson 2", "lesson 3"],
  "claim_boundary": "short paragraph"
}}
""".strip()


def _normalize(model: str, parsed: dict[str, Any]) -> dict[str, Any]:
    per_paper = parsed.get("per_paper") or []
    winners = [item.get("winner") for item in per_paper]
    baseline_scores = []
    guided_scores = []
    for item in per_paper:
        scores = item.get("scores") or {}
        baseline = scores.get("baseline") or {}
        guided = scores.get("review_guided") or {}
        if isinstance(baseline.get("overall"), (int, float)):
            baseline_scores.append(float(baseline["overall"]))
        if isinstance(guided.get("overall"), (int, float)):
            guided_scores.append(float(guided["overall"]))
    mean_baseline = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
    mean_guided = sum(guided_scores) / len(guided_scores) if guided_scores else 0.0
    parsed["model"] = model
    parsed["aggregate"] = {
        "review_guided_wins": sum(1 for winner in winners if winner == "review_guided"),
        "baseline_wins": sum(1 for winner in winners if winner == "baseline"),
        "ties": sum(1 for winner in winners if winner == "tie"),
        "mean_baseline_overall": round(mean_baseline, 4),
        "mean_review_guided_overall": round(mean_guided, 4),
        "mean_delta_review_guided_minus_baseline": round(mean_guided - mean_baseline, 4),
    }
    return parsed


def _aggregate_reviews(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {
        "model_count": len(reviews),
        "review_guided_wins": 0,
        "baseline_wins": 0,
        "ties": 0,
        "mean_baseline_overall_by_model": [],
        "mean_review_guided_overall_by_model": [],
        "mean_delta_by_model": [],
    }
    per_paper_votes: dict[str, dict[str, int]] = {}
    for review in reviews:
        agg = review.get("aggregate", {})
        totals["review_guided_wins"] += int(agg.get("review_guided_wins", 0))
        totals["baseline_wins"] += int(agg.get("baseline_wins", 0))
        totals["ties"] += int(agg.get("ties", 0))
        totals["mean_baseline_overall_by_model"].append(agg.get("mean_baseline_overall"))
        totals["mean_review_guided_overall_by_model"].append(agg.get("mean_review_guided_overall"))
        totals["mean_delta_by_model"].append(agg.get("mean_delta_review_guided_minus_baseline"))
        for item in review.get("per_paper", []):
            votes = per_paper_votes.setdefault(item.get("paper_id", "unknown"), {"review_guided": 0, "baseline": 0, "tie": 0})
            winner = item.get("winner")
            if winner in votes:
                votes[winner] += 1
    totals["per_paper_votes"] = per_paper_votes
    numeric_deltas = [value for value in totals["mean_delta_by_model"] if isinstance(value, (int, float))]
    totals["mean_delta_across_models"] = round(sum(numeric_deltas) / len(numeric_deltas), 4) if numeric_deltas else 0.0
    return totals


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# OpenReview Regeneration Cross-Model Review",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Source summary: `{summary['source_summary']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Models: `{', '.join(summary['models'])}`",
        f"- Pair count: `{summary['pair_count']}`",
        "",
        "## Aggregate",
        "",
        f"- Review-guided wins: `{summary['aggregate']['review_guided_wins']}`",
        f"- Baseline wins: `{summary['aggregate']['baseline_wins']}`",
        f"- Ties: `{summary['aggregate']['ties']}`",
        f"- Mean delta across models: `{summary['aggregate']['mean_delta_across_models']}`",
        "",
        "## Model Results",
        "",
        "| Model | Review-guided wins | Baseline wins | Ties | Mean delta |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for review in summary["reviews"]:
        agg = review["aggregate"]
        lines.append(
            f"| {review['model']} | {agg['review_guided_wins']} | {agg['baseline_wins']} | "
            f"{agg['ties']} | {agg['mean_delta_review_guided_minus_baseline']} |"
        )
    lines.extend(["", "## Per-Paper Votes", "", "| Paper ID | Review-guided | Baseline | Tie |", "| --- | ---: | ---: | ---: |"])
    for paper_id, votes in summary["aggregate"]["per_paper_votes"].items():
        lines.append(f"| {paper_id} | {votes['review_guided']} | {votes['baseline']} | {votes['tie']} |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
        ]
    )
    return "\n".join(lines) + "\n"


def _write(path: Path, text: str) -> str:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_cross_model_openreview_regeneration_review"
    manifest["openreview_regeneration_cross_model_review"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "models": summary["models"],
        "pair_count": summary["pair_count"],
        "review_guided_wins": summary["aggregate"]["review_guided_wins"],
        "baseline_wins": summary["aggregate"]["baseline_wins"],
        "ties": summary["aggregate"]["ties"],
        "mean_delta_across_models": summary["aggregate"]["mean_delta_across_models"],
        "claim_boundary": summary["claim_boundary"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"openreview_regeneration_cross_model_review_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--source-summary", default=str(DEFAULT_SOURCE))
    parser.add_argument("--models", nargs="+", default=["claude-3-7-sonnet-latest"])
    parser.add_argument("--max-tokens", type=int, default=7000)
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    source_path = Path(args.source_summary)
    if not source_path.is_absolute():
        source_path = ROOT / source_path
    source = _load_json(source_path)
    compact = _compact_source(source)
    prompt = _review_prompt(compact)

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    reviews = []
    paths = [
        _write(out_dir / "source_compact.json", json.dumps(compact, ensure_ascii=False, indent=2)),
        _write(out_dir / "review_prompt.txt", prompt),
    ]
    for model in args.models:
        response = _call_monica(
            model=model,
            messages=[
                {"role": "system", "content": "Return strict JSON. Score conservatively and independently."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=args.max_tokens,
            temperature=0.1,
        )
        raw_text = _message_text(response)
        parsed = _normalize(model, _extract_json_object(raw_text))
        parsed["latency_seconds"] = response.get("_latency_seconds")
        parsed["attempts"] = response.get("_attempts")
        safe_model = model.replace("/", "_").replace(":", "_")
        paths.extend(
            [
                _write(out_dir / f"{safe_model}_raw_response.txt", raw_text),
                _write(out_dir / f"{safe_model}_review.json", json.dumps(parsed, ensure_ascii=False, indent=2)),
            ]
        )
        reviews.append(parsed)

    summary: dict[str, Any] = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "openreview_regeneration_cross_model_review",
        "source_summary": _rel(source_path),
        "models": args.models,
        "pair_count": len(compact["pairs"]),
        "reviews": reviews,
        "aggregate": _aggregate_reviews(reviews),
        "claim_boundary": (
            "Cross-model review reduces same-model scoring bias for regenerated "
            "mini-paper artifacts, but it is still model-routed artifact review, "
            "not independent human peer review or experiment rerun."
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
    _update_manifest(paths + ["scripts/run_openreview_regeneration_cross_model_review.py"], summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
