#!/usr/bin/env python3
"""Compare human-participation modes using an OpenReview-derived proxy rubric.

This probe turns the OpenReview taste-prior data probe into a workflow-design
experiment. It asks one model to generate same-task artifacts under several
participation modes, then asks a fixed scorer to evaluate them against a rubric
conditioned on sampled OpenReview high/low review examples.

The result is an offline participation-mode selection signal only. It is not a
live human-subject study, not independent peer review, and not evidence of
real-world acceptance.
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


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXPERT_PROBE_DIR = DOC_DIR / "experiments" / "expert_review_taste_prior_probe_20260602_031800"
MODE_IDS = [
    "no_human_gate",
    "taste_prior_gate",
    "evaluator_stress_gate",
    "structured_feedback_gate",
    "claim_calibration_gate",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path, max_chars: int) -> str:
    return path.read_text(encoding="utf-8")[:max_chars]


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
    with request.urlopen(req, timeout=180) as resp:  # noqa: S310 - fixed HTTPS API endpoint.
        payload = json.loads(resp.read().decode("utf-8"))
    payload["_latency_seconds"] = round(time.time() - started, 3)
    return payload


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


def _openreview_exemplars() -> dict[str, Any]:
    summary = _load_json(EXPERT_PROBE_DIR / "summary.json")
    high = _load_json(EXPERT_PROBE_DIR / "high_score_examples.json")[:3]
    low = _load_json(EXPERT_PROBE_DIR / "low_score_examples.json")[:3]
    compact = {
        "dataset": summary["dataset"],
        "sample_size": summary["sample_size"],
        "score_summary": summary["score_summary"],
        "high_score_examples": [
            {
                "title": row.get("title"),
                "mean_score": row.get("mean_score"),
                "decision": row.get("decision"),
                "abstract_excerpt": row.get("abstract_excerpt", "")[:500],
                "review_snippets": [snippet[:350] for snippet in row.get("review_snippets", [])[:2]],
            }
            for row in high
        ],
        "low_score_examples": [
            {
                "title": row.get("title"),
                "mean_score": row.get("mean_score"),
                "decision": row.get("decision"),
                "abstract_excerpt": row.get("abstract_excerpt", "")[:500],
                "review_snippets": [snippet[:350] for snippet in row.get("review_snippets", [])[:2]],
            }
            for row in low
        ],
    }
    return compact


def _generation_prompt() -> str:
    problem = _read(DOC_DIR / "problem_statement.md", 2500)
    readiness = _read(DOC_DIR / "audits" / "top_conference_readiness_audit.md", 4500)
    paper_intro = _read(DOC_DIR / "paper_en.md", 4500)
    return f"""
You are generating matched workflow artifacts for a participation-mode
selection experiment.

Task: improve the Co-Pilot AI Scientist v3 paper package. Each mode must produce
a short research artifact for the same task: a next-step proposal containing
problem framing, intervention pattern, minimal experiment, expected evidence,
risks, and claim boundary.

Modes to compare:
- no_human_gate: fully autonomous AI Scientist-v2-style planning.
- taste_prior_gate: human scientific taste is injected before experiment search.
- evaluator_stress_gate: human insight stress-tests metrics and failure modes.
- structured_feedback_gate: human feedback is structured by rubric before manuscript revision.
- claim_calibration_gate: human intervention focuses on weakening or reframing unsupported claims.

Current problem statement:
{problem}

Current readiness audit excerpt:
{readiness}

Current paper opening excerpt:
{paper_intro}

Return strict JSON only:
{{
  "artifacts": [
    {{
      "mode_id": "one of the five ids",
      "title": "...",
      "problem_framing": "...",
      "participation_pattern": "...",
      "minimal_experiment": "...",
      "expected_evidence": ["..."],
      "risk_and_failure_value": "...",
      "claim_boundary": "...",
      "artifact_text": "A 180-260 word proposal written as if it were a paper-method subsection."
    }}
  ]
}}
Return exactly one artifact per mode.
""".strip()


def _scoring_prompt(artifacts: dict[str, Any], exemplars: dict[str, Any]) -> str:
    return f"""
You are an offline expert-review proxy scorer. Score participation-mode
artifacts for the Co-Pilot AI Scientist v3 paper. Your rubric is inspired by
sampled OpenReview expert-review data, not by live human peer review.

Use these OpenReview-derived dimensions:
- novelty: does the artifact point toward a nontrivial research contribution?
- correctness: is the proposed experiment logically valid and not metric-gamed?
- clarity: is the workflow easy to understand and reproduce?
- impact: would this mode plausibly improve human-AI research collaboration?
- confidence: how confident are you in the score from the artifact alone?
- claim_calibration: does it avoid overclaiming?
- workflow_utility: does it help decide a better human participation pattern?

OpenReview-derived context:
{json.dumps(exemplars, ensure_ascii=False, indent=2)}

Artifacts to score:
{json.dumps(artifacts, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "ranking": ["best_mode", "..."],
  "scores": {{
    "mode_id": {{
      "novelty": 1-5,
      "correctness": 1-5,
      "clarity": 1-5,
      "impact": 1-5,
      "confidence": 1-5,
      "claim_calibration": 1-5,
      "workflow_utility": 1-5,
      "overall": 1-5
    }}
  }},
  "best_mode": "mode_id",
  "worst_mode": "mode_id",
  "mode_design_lessons": ["lesson 1", "lesson 2", "lesson 3"],
  "why_best_mode_wins": "short paragraph",
  "where_best_mode_can_fail": ["failure mode"],
  "claim_boundary": "short paragraph"
}}
""".strip()


def _markdown(summary: dict[str, Any]) -> str:
    scores = summary["scoring"].get("scores", {})
    lines = [
        "# Participation-Mode Selection Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Model: `{summary['model']}`",
        f"- Live model calls: `{summary['live_model_calls']}`",
        f"- Expert-review proxy: `{summary['expert_review_proxy']}`",
        f"- Best mode: `{summary['scoring'].get('best_mode')}`",
        f"- Worst mode: `{summary['scoring'].get('worst_mode')}`",
        "",
        "## Scope",
        "",
        summary["scope_note"],
        "",
        "## Score Table",
        "",
        "| Mode | Novelty | Correctness | Clarity | Impact | Confidence | Claim calibration | Workflow utility | Overall |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode in MODE_IDS:
        row = scores.get(mode, {})
        lines.append(
            f"| {mode} | {row.get('novelty', 'n/a')} | {row.get('correctness', 'n/a')} | "
            f"{row.get('clarity', 'n/a')} | {row.get('impact', 'n/a')} | "
            f"{row.get('confidence', 'n/a')} | {row.get('claim_calibration', 'n/a')} | "
            f"{row.get('workflow_utility', 'n/a')} | {row.get('overall', 'n/a')} |"
        )
    lines.extend(
        [
            "",
            "## Ranking",
            "",
            ", ".join(f"`{mode}`" for mode in summary["scoring"].get("ranking", [])),
            "",
            "## Why The Best Mode Wins",
            "",
            summary["scoring"].get("why_best_mode_wins", "n/a"),
            "",
            "## Mode Design Lessons",
            "",
        ]
    )
    for lesson in summary["scoring"].get("mode_design_lessons", []):
        lines.append(f"- {lesson}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            summary["scoring"].get("claim_boundary", ""),
            "",
            "This is an offline, model-routed participation-mode selection probe",
            "conditioned on sampled OpenReview review examples. It is not live",
            "human peer review and does not prove final paper-quality gains.",
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
    manifest["status"] = "pilot_package_with_participation_mode_selection_probe"
    manifest["participation_mode_selection_probe"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "expert_review_proxy": summary["expert_review_proxy"],
        "best_mode": summary["scoring"].get("best_mode"),
        "ranking": summary["scoring"].get("ranking", []),
        "claim_boundary": "Offline OpenReview-derived model-routed workflow-selection probe only.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"participation_mode_selection_probe_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--max-tokens", type=int, default=4096)
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    generation_prompt = _generation_prompt()
    generation_response = _call_monica(
        model=args.model,
        messages=[
            {"role": "system", "content": "Return strict JSON. Keep claims conservative and evidence-bound."},
            {"role": "user", "content": generation_prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.45,
    )
    generation_text = _message_text(generation_response)
    artifacts = _extract_json_object(generation_text)

    exemplars = _openreview_exemplars()
    scoring_prompt = _scoring_prompt(artifacts, exemplars)
    scoring_response = _call_monica(
        model=args.model,
        messages=[
            {"role": "system", "content": "Return strict JSON. You are a conservative research-workflow auditor."},
            {"role": "user", "content": scoring_prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.1,
    )
    scoring_text = _message_text(scoring_response)
    scoring = _extract_json_object(scoring_text)

    summary: dict[str, Any] = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "participation_mode_selection_probe",
        "model": args.model,
        "live_model_calls": 2,
        "expert_review_proxy": "nhop/OpenReview sampled high/low examples from expert_review_taste_prior_probe_20260602_031800",
        "scope_note": (
            "Same-task offline comparison of five human-participation modes. "
            "Scores are model-routed and OpenReview-conditioned; they are not "
            "independent human expert review or downstream benchmark evidence."
        ),
        "mode_ids": MODE_IDS,
        "generation_latency_seconds": generation_response.get("_latency_seconds"),
        "scoring_latency_seconds": scoring_response.get("_latency_seconds"),
        "artifacts": artifacts,
        "scoring": scoring,
    }

    paths = [
        _write(out_dir / "generation_prompt.txt", generation_prompt),
        _write(out_dir / "generation_raw_response.txt", generation_text),
        _write(out_dir / "mode_artifacts.json", json.dumps(artifacts, ensure_ascii=False, indent=2)),
        _write(out_dir / "scoring_prompt.txt", scoring_prompt),
        _write(out_dir / "scoring_raw_response.txt", scoring_text),
        _write(out_dir / "openreview_exemplars_compact.json", json.dumps(exemplars, ensure_ascii=False, indent=2)),
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
    _update_manifest(paths + ["scripts/run_participation_mode_selection_probe.py"], summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
