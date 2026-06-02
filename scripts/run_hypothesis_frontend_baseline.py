#!/usr/bin/env python3
"""Compare IGRE hypothesis-frontier generation with an autonomous front end.

The probe reuses the archived IGRE hypothesis-frontier smoke and generates a
same-model autonomous AI Scientist-v2-style candidate portfolio without the
IGRE human-taste framing. A fixed-rubric model call then compares the two
portfolios. This is front-end measurement evidence only, not a benchmark result
or independent expert review.
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
DEFAULT_IGRE_SUMMARY = (
    DOC_DIR / "experiments" / "hypothesis_frontier_smoke_20260602_021500" / "summary.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path, max_chars: int = 6000) -> str:
    return path.read_text(encoding="utf-8")[:max_chars]


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
    with request.urlopen(req, timeout=120) as resp:  # noqa: S310 - fixed HTTPS API endpoint.
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


def _autonomous_generation_prompt() -> str:
    problem = _read(DOC_DIR / "problem_statement.md", 3200)
    readiness = _read(DOC_DIR / "audits" / "top_conference_readiness_audit.md", 5000)
    benchmark = _read(DOC_DIR / "benchmark_claim_matrix.md", 3500)
    return f"""
You are an autonomous AI Scientist-v2-style hypothesis front end. Generate
candidate research directions for improving the current Co-Pilot AI Scientist
v3 paper package.

Important constraints:
- Do not use the IGRE human-taste framing as an explicit method.
- Do not add human decision gates, human taste priors, or structured human
  feedback as the central mechanism.
- Do not claim the current system already outperforms autonomous AI Scientist-v2.
- Prefer runnable experiments, benchmark fit, and conservative claims.
- Return strict JSON only.

Current problem statement excerpt:
{problem}

Current readiness audit excerpt:
{readiness}

Benchmark-to-claim excerpt:
{benchmark}

Return a JSON object with:
{{
  "frontier_candidates": [
    {{
      "id": "auto_frontier_short_id",
      "title": "...",
      "core_hypothesis": "...",
      "why_now": "...",
      "claim_it_tests": "...",
      "minimal_experiment": "...",
      "benchmark_or_evaluator": "...",
      "expected_artifacts": ["..."],
      "main_risk": "...",
      "failure_value": "..."
    }}
  ]
}}
Generate exactly 4 candidates.
""".strip()


def _comparison_prompt(igre_summary: dict[str, Any], autonomous: dict[str, Any]) -> str:
    return f"""
You are a strict research-frontier portfolio auditor. Compare two same-model
hypothesis-frontier portfolios for the Co-Pilot AI Scientist v3 paper.

Portfolio A is the archived IGRE front end. It explicitly uses human scientific
taste/insight as a high-variance search prior.
Portfolio B is an autonomous AI Scientist-v2-style front end. It avoids explicit
human taste gates and structured human feedback.

Score the portfolios as research-planning artifacts only. Do not infer benchmark
performance or paper quality beyond the supplied text.

Return strict JSON only:
{{
  "recommendation": "IGRE" | "autonomous" | "tie",
  "scores": {{
    "IGRE": {{
      "evidence_gain": 1-5,
      "benchmark_fit": 1-5,
      "method_distinctness": 1-5,
      "human_taste_visibility": 1-5,
      "feasibility": 1-5,
      "claim_calibration": 1-5,
      "novelty_risk_balance": 1-5,
      "overall": 1-5
    }},
    "autonomous": {{
      "evidence_gain": 1-5,
      "benchmark_fit": 1-5,
      "method_distinctness": 1-5,
      "human_taste_visibility": 1-5,
      "feasibility": 1-5,
      "claim_calibration": 1-5,
      "novelty_risk_balance": 1-5,
      "overall": 1-5
    }}
  }},
  "best_IGRE_candidate": "...",
  "best_autonomous_candidate": "...",
  "rationale": "short paragraph",
  "where_autonomous_is_stronger": ["..."],
  "where_IGRE_is_stronger": ["..."],
  "required_next_evidence": ["item 1", "item 2", "item 3"],
  "claim_boundary": "..."
}}

Portfolio A, IGRE:
{json.dumps(igre_summary, ensure_ascii=False, indent=2)}

Portfolio B, autonomous:
{json.dumps(autonomous, ensure_ascii=False, indent=2)}
""".strip()


def _write(path: Path, text: str) -> str:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _markdown(summary: dict[str, Any]) -> str:
    score = summary["comparison"]
    scores = score.get("scores", {})
    igre = scores.get("IGRE", {}) if isinstance(scores, dict) else {}
    auto = scores.get("autonomous", {}) if isinstance(scores, dict) else {}
    lines = [
        "# Hypothesis Front-End Baseline Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Provider: `{summary['provider']}`",
        f"- Model: `{summary['model']}`",
        f"- Live model calls: `{summary['live_model_calls']}`",
        f"- Archived IGRE summary: `{summary['igre_summary']}`",
        f"- Recommendation: `{score.get('recommendation', 'unparsed')}`",
        f"- Best IGRE candidate: `{score.get('best_IGRE_candidate', 'n/a')}`",
        f"- Best autonomous candidate: `{score.get('best_autonomous_candidate', 'n/a')}`",
        "",
        "## Scope",
        "",
        summary["scope_note"],
        "",
        "## Score Table",
        "",
        "| Dimension | IGRE | Autonomous |",
        "| --- | ---: | ---: |",
    ]
    for key in [
        "evidence_gain",
        "benchmark_fit",
        "method_distinctness",
        "human_taste_visibility",
        "feasibility",
        "claim_calibration",
        "novelty_risk_balance",
        "overall",
    ]:
        lines.append(f"| {key} | {igre.get(key, 'n/a')} | {auto.get(key, 'n/a')} |")
    lines.extend(
        [
            "",
            "## Rationale",
            "",
            str(score.get("rationale", "No parsed rationale.")),
            "",
            "## Required Next Evidence",
            "",
        ]
    )
    for item in score.get("required_next_evidence", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            score.get("claim_boundary", "Not supplied."),
            "",
            "This probe compares front-end research direction portfolios only. It",
            "does not evaluate downstream benchmark performance, final paper quality,",
            "or human expert judgment.",
        ]
    )
    return "\n".join(lines) + "\n"


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_hypothesis_frontend_baseline"
    manifest["hypothesis_frontend_baseline_probe"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "recommendation": summary["comparison"].get("recommendation"),
        "scope_note": summary["scope_note"],
        "live_model_calls": summary["live_model_calls"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"hypothesis_frontend_baseline_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--igre-summary", default=str(DEFAULT_IGRE_SUMMARY))
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--max-tokens", type=int, default=1800)
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    igre_path = Path(args.igre_summary)
    if not igre_path.is_absolute():
        igre_path = ROOT / igre_path
    out_dir = Path(args.output_dir) if args.output_dir else DOC_DIR / "experiments" / args.run_id
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    igre_summary = json.loads(igre_path.read_text(encoding="utf-8"))
    autonomous_prompt = _autonomous_generation_prompt()
    autonomous_response = _call_monica(
        model=args.model,
        messages=[
            {
                "role": "system",
                "content": "You generate rigorous, testable research directions as strict JSON.",
            },
            {"role": "user", "content": autonomous_prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.3,
    )
    autonomous_text = _message_text(autonomous_response)
    autonomous = _extract_json_object(autonomous_text)

    comparison_prompt = _comparison_prompt(igre_summary, autonomous)
    comparison_response = _call_monica(
        model=args.model,
        messages=[
            {
                "role": "system",
                "content": "You are a conservative research-frontier auditor. Return valid JSON only.",
            },
            {"role": "user", "content": comparison_prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.05,
    )
    comparison_text = _message_text(comparison_response)
    comparison = _extract_json_object(comparison_text)

    paths: list[str] = []
    paths.append(_write(out_dir / "autonomous_generation_prompt.txt", autonomous_prompt))
    paths.append(_write(out_dir / "autonomous_raw_response.txt", autonomous_text))
    paths.append(_write(out_dir / "autonomous_candidates.json", json.dumps(autonomous, ensure_ascii=False, indent=2)))
    paths.append(_write(out_dir / "comparison_prompt.txt", comparison_prompt))
    paths.append(_write(out_dir / "comparison_raw_response.txt", comparison_text))
    paths.append(
        _write(
            out_dir / "model_responses.json",
            json.dumps(
                {
                    "autonomous_generation": autonomous_response,
                    "comparison": comparison_response,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
    )
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "hypothesis_frontend_baseline_probe",
        "provider": "Monica OpenAI-compatible API",
        "model": args.model,
        "live_model_calls": 2,
        "igre_summary": _rel(igre_path),
        "summary_path": _rel(out_dir / "summary.json"),
        "scope_note": (
            "Same-model front-end portfolio comparison between archived IGRE "
            "hypothesis generation and an autonomous AI Scientist-v2-style "
            "baseline. This is direction-finding evidence only, not downstream "
            "benchmark or paper-quality evidence."
        ),
        "autonomous_generation_latency_seconds": autonomous_response.get("_latency_seconds"),
        "comparison_latency_seconds": comparison_response.get("_latency_seconds"),
        "autonomous_generation": autonomous,
        "comparison": comparison,
        "artifacts": paths,
    }
    paths.append(_write(out_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2)))
    paths.append(_write(out_dir / "README.md", _markdown(summary)))
    summary["artifacts"] = paths
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _update_manifest(paths + ["scripts/run_hypothesis_frontend_baseline.py"], summary)
    print(json.dumps({"summary": summary["summary_path"], "recommendation": comparison.get("recommendation")}, indent=2))


if __name__ == "__main__":
    main()
