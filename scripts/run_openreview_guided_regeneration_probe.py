#!/usr/bin/env python3
"""Regenerate ML/AI paper artifacts with and without real OpenReview feedback.

This probe uses real OpenReview review text as a concrete form of human
scientific taste/insight. For three ML/AI papers sampled from the local
OpenReview probe, it asks the same model to produce a baseline regenerated
mini-paper artifact from title/abstract only and a review-guided artifact from
title/abstract plus review comments. A fixed scorer then compares each pair.

The probe is evidence for whether review-guided human insight can improve
paper-shaped artifacts under a model-routed rubric. It is not a claim of actual
paper acceptance, full experiment rerun, or independent expert review.
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
from urllib.error import HTTPError, URLError
from urllib import request


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXPERT_PROBE_DIR = DOC_DIR / "experiments" / "expert_review_taste_prior_probe_20260602_031800"
DEFAULT_INDICES = [1, 34, 49]


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
            with request.urlopen(req, timeout=180) as resp:  # noqa: S310 - fixed HTTPS API endpoint.
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


def _compact_paper(row: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "paper_id": f"openreview_sample_{index}",
        "sample_index": index,
        "title": row.get("title"),
        "venue": row.get("venue"),
        "arxiv_id": row.get("arxiv_id"),
        "decision": row.get("decision"),
        "mean_score": row.get("mean_score"),
        "mean_novelty": row.get("mean_novelty"),
        "mean_correctness": row.get("mean_correctness"),
        "mean_clarity": row.get("mean_clarity"),
        "mean_impact": row.get("mean_impact"),
        "abstract_excerpt": (row.get("abstract_excerpt") or "")[:1100],
        "decision_text_excerpt": (row.get("decision_text_excerpt") or "")[:900],
        "review_snippets": [(snippet or "")[:900] for snippet in (row.get("review_snippets") or [])[:3]],
    }


def _select_papers(indices: list[int]) -> list[dict[str, Any]]:
    rows = _load_json(EXPERT_PROBE_DIR / "sample_rows_compact.json")
    selected = []
    for index in indices:
        if index < 0 or index >= len(rows):
            raise ValueError(f"sample index out of range: {index}")
        selected.append(_compact_paper(rows[index], index))
    return selected


def _generation_prompt(papers: list[dict[str, Any]]) -> str:
    return f"""
You are running a controlled OpenReview-guided paper-regeneration probe.

For each selected ML/AI paper, generate two mini-paper artifacts:

1. baseline_regeneration: use only title and abstract. Do not use review
   snippets or decision text.
2. review_guided_regeneration: use title, abstract, and the real OpenReview
   review snippets/decision text as human scientific taste and insight. Address
   reviewer concerns explicitly.

Each artifact should be a short paper-shaped proposal with:
- revised core contribution,
- method sketch,
- experiment plan,
- expected evidence,
- limitations and claim boundary.

Do not invent completed experimental results. Write as a revised research plan
or mini-paper proposal, not as an accepted final paper.

Selected papers:
{json.dumps(papers, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "papers": [
    {{
      "paper_id": "...",
      "title": "...",
      "baseline_regeneration": {{
        "core_contribution": "...",
        "method_sketch": "...",
        "experiment_plan": "...",
        "limitations": "...",
        "claim_boundary": "...",
        "mini_paper_artifact": "220-320 words"
      }},
      "review_guided_regeneration": {{
        "review_insights_used": ["..."],
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
Return exactly one object for each selected paper.
""".strip()


def _scoring_prompt(papers: list[dict[str, Any]], regenerations: dict[str, Any]) -> str:
    return f"""
You are a conservative paper-quality auditor. Compare baseline and
review-guided regenerations for each OpenReview paper.

The review-guided version is allowed to use real review text as human
scientific taste/insight. The baseline version only had title and abstract.
Judge whether the review-guided artifact makes better use of problem framing,
method design, experiment planning, limitation honesty, and claim calibration.

Important: this is not peer review and not a full experiment rerun. Score only
the generated mini-paper artifacts.

Source paper metadata and review snippets:
{json.dumps(papers, ensure_ascii=False, indent=2)}

Generated artifacts:
{json.dumps(regenerations, ensure_ascii=False, indent=2)}

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
      "review_insight_effect": "short explanation",
      "remaining_risk": "short explanation"
    }}
  ],
  "aggregate": {{
    "review_guided_wins": 0,
    "baseline_wins": 0,
    "ties": 0,
    "mean_baseline_overall": 0.0,
    "mean_review_guided_overall": 0.0,
    "mean_delta_review_guided_minus_baseline": 0.0
  }},
  "design_lessons": ["lesson 1", "lesson 2", "lesson 3"],
  "claim_boundary": "short paragraph"
}}
""".strip()


def _normalize_scoring(scoring: dict[str, Any]) -> dict[str, Any]:
    """Recompute aggregate fields from per-paper scores.

    Model outputs sometimes round aggregate means too aggressively. The
    per-paper judgments are the authoritative scored units, so keep the model's
    design lessons and rationales but derive aggregate counts/means
    deterministically.
    """
    per_paper = scoring.get("per_paper") or []
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
    scoring["aggregate"] = {
        "review_guided_wins": sum(1 for winner in winners if winner == "review_guided"),
        "baseline_wins": sum(1 for winner in winners if winner == "baseline"),
        "ties": sum(1 for winner in winners if winner == "tie"),
        "mean_baseline_overall": round(mean_baseline, 4),
        "mean_review_guided_overall": round(mean_guided, 4),
        "mean_delta_review_guided_minus_baseline": round(mean_guided - mean_baseline, 4),
    }
    return scoring


def _markdown(summary: dict[str, Any]) -> str:
    aggregate = summary["scoring"].get("aggregate", {})
    lines = [
        "# OpenReview-Guided Regeneration Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Model: `{summary['model']}`",
        f"- Live model calls: `{summary['live_model_calls']}`",
        f"- Selected papers: `{len(summary['selected_papers'])}`",
        f"- Review-guided wins: `{aggregate.get('review_guided_wins')}`",
        f"- Baseline wins: `{aggregate.get('baseline_wins')}`",
        f"- Ties: `{aggregate.get('ties')}`",
        f"- Mean baseline overall: `{aggregate.get('mean_baseline_overall')}`",
        f"- Mean review-guided overall: `{aggregate.get('mean_review_guided_overall')}`",
        f"- Mean delta: `{aggregate.get('mean_delta_review_guided_minus_baseline')}`",
        "",
        "## Scope",
        "",
        summary["scope_note"],
        "",
        "## Selected Papers",
        "",
    ]
    for paper in summary["selected_papers"]:
        lines.append(
            f"- `{paper['paper_id']}` | score={paper.get('mean_score')} | "
            f"decision={paper.get('decision')} | {paper.get('title')}"
        )
    lines.extend(["", "## Pairwise Results", ""])
    for item in summary["scoring"].get("per_paper", []):
        base = item.get("scores", {}).get("baseline", {})
        guided = item.get("scores", {}).get("review_guided", {})
        lines.append(
            f"- `{item.get('paper_id')}` winner=`{item.get('winner')}`; "
            f"baseline overall={base.get('overall')}; "
            f"review-guided overall={guided.get('overall')}; "
            f"effect={item.get('review_insight_effect')}"
        )
    lines.extend(["", "## Design Lessons", ""])
    for lesson in summary["scoring"].get("design_lessons", []):
        lines.append(f"- {lesson}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            summary["scoring"].get("claim_boundary", ""),
            "",
            "This probe uses real review text as human scientific taste/insight,",
            "but it regenerates paper-shaped artifacts only. It does not rerun the",
            "original experiments or constitute independent peer review.",
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
    manifest["status"] = "pilot_package_with_openreview_guided_regeneration_probe"
    aggregate = summary["scoring"].get("aggregate", {})
    manifest["openreview_guided_regeneration_probe"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "selected_papers": len(summary["selected_papers"]),
        "review_guided_wins": aggregate.get("review_guided_wins"),
        "baseline_wins": aggregate.get("baseline_wins"),
        "ties": aggregate.get("ties"),
        "mean_delta_review_guided_minus_baseline": aggregate.get("mean_delta_review_guided_minus_baseline"),
        "claim_boundary": "Real OpenReview text used as human taste/insight, but regenerated mini-paper artifacts only.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"openreview_guided_regeneration_probe_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--indices", default=",".join(str(i) for i in DEFAULT_INDICES))
    parser.add_argument("--max-tokens", type=int, default=6000)
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    indices = [int(part.strip()) for part in args.indices.split(",") if part.strip()]
    selected = _select_papers(indices)
    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    generation_prompt = _generation_prompt(selected)
    generation_response = _call_monica(
        model=args.model,
        messages=[
            {"role": "system", "content": "Return strict JSON. Keep all claims evidence-bound."},
            {"role": "user", "content": generation_prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.35,
    )
    generation_text = _message_text(generation_response)
    regenerations = _extract_json_object(generation_text)

    scoring_prompt = _scoring_prompt(selected, regenerations)
    scoring_response = _call_monica(
        model=args.model,
        messages=[
            {"role": "system", "content": "Return strict JSON. Score conservatively."},
            {"role": "user", "content": scoring_prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.1,
    )
    scoring_text = _message_text(scoring_response)
    scoring = _normalize_scoring(_extract_json_object(scoring_text))

    summary: dict[str, Any] = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "openreview_guided_regeneration_probe",
        "model": args.model,
        "live_model_calls": 2,
        "scope_note": (
            f"{len(selected)} selected ML/AI OpenReview papers are regenerated twice: "
            "from title/abstract only, and from title/abstract plus real "
            "OpenReview review comments as human scientific taste/insight. "
            "The comparison scores mini-paper artifacts only."
        ),
        "selected_indices": indices,
        "selected_papers": selected,
        "generation_latency_seconds": generation_response.get("_latency_seconds"),
        "scoring_latency_seconds": scoring_response.get("_latency_seconds"),
        "regenerations": regenerations,
        "scoring": scoring,
    }

    paths = [
        _write(out_dir / "selected_papers.json", json.dumps(selected, ensure_ascii=False, indent=2)),
        _write(out_dir / "generation_prompt.txt", generation_prompt),
        _write(out_dir / "generation_raw_response.txt", generation_text),
        _write(out_dir / "regenerated_artifacts.json", json.dumps(regenerations, ensure_ascii=False, indent=2)),
        _write(out_dir / "scoring_prompt.txt", scoring_prompt),
        _write(out_dir / "scoring_raw_response.txt", scoring_text),
    ]
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
    _update_manifest(paths + ["scripts/run_openreview_guided_regeneration_probe.py"], summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
