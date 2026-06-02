#!/usr/bin/env python3
"""Run a small Monica-routed hypothesis-frontier smoke for IGRE.

This script is evidence-shape tooling for the AI Co-Scientist-style front end:
generate candidate research directions, critique/rank them, and archive the
model responses. It is not a benchmark result and does not prove paper quality.
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


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read(path: Path, max_chars: int = 6000) -> str:
    return path.read_text(encoding="utf-8")[:max_chars]


def _call_monica(model: str, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> dict[str, Any]:
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
    with request.urlopen(req, timeout=90) as resp:  # noqa: S310 - fixed HTTPS endpoint, no user URL.
        payload = json.loads(resp.read().decode("utf-8"))
    payload["_latency_seconds"] = round(time.time() - started, 3)
    return payload


def _message_text(response: dict[str, Any]) -> str:
    return response["choices"][0]["message"]["content"]


def _extract_json_object(text: str) -> dict[str, Any]:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    if fenced:
        return json.loads(fenced.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("model response does not contain a JSON object")
    return json.loads(text[start : end + 1])


def _generation_prompt() -> str:
    problem = _read(DOC_DIR / "problem_statement.md", 3000)
    readiness = _read(DOC_DIR / "audits" / "top_conference_readiness_audit.md", 5000)
    benchmark = _read(DOC_DIR / "benchmark_claim_matrix.md", 3500)
    return f"""
You are the AI Co-Scientist-style hypothesis-generation front end for an IGRE
(Insight-Gated Research Evolution) paper. Generate fresh candidate research
frontiers for improving the current Co-Pilot AI Scientist v3 package.

Constraints:
- Do not claim the system already outperforms autonomous AI Scientist-v2.
- Prefer directions that create auditable evidence, not cosmetic prose.
- Human scientific taste should be treated as a high-variance search prior,
  not as generic approval or a guaranteed improvement.
- Benchmarks must be claim-matched and may go beyond FML-bench.
- Return strict JSON only.

Current problem statement excerpt:
{problem}

Current top-conference readiness excerpt:
{readiness}

Benchmark-to-claim excerpt:
{benchmark}

Return a JSON object with:
{{
  "frontier_candidates": [
    {{
      "id": "frontier_short_id",
      "title": "...",
      "core_hypothesis": "...",
      "why_now": "...",
      "claim_it_tests": "...",
      "minimal_experiment": "...",
      "benchmark_or_evaluator": "...",
      "human_taste_role": "...",
      "expected_artifacts": ["..."],
      "main_risk": "...",
      "failure_value": "..."
    }}
  ]
}}
Generate exactly 4 candidates.
""".strip()


def _critique_prompt(candidates: dict[str, Any]) -> str:
    return f"""
Critique and rank these IGRE research-frontier candidates. Use the same evidence
discipline as AI Scientist-v2: narrow claims, benchmark fit, runnable
experiments, ablations, failure value, and reproducibility. Also score whether
the candidate makes human scientific taste/insight visible rather than merely
adding generic human approval.

Return strict JSON only:
{{
  "ranking": [
    {{
      "id": "...",
      "overall_score": 1-5,
      "evidence_gain": 1-5,
      "benchmark_fit": 1-5,
      "human_taste_visibility": 1-5,
      "cost_risk": 1-5,
      "reason": "..."
    }}
  ],
  "selected_for_next_budget": "...",
  "selection_rationale": "...",
  "claim_boundary": "..."
}}

Candidates:
{json.dumps(candidates, ensure_ascii=False, indent=2)}
""".strip()


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Hypothesis Frontier Smoke",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Provider: `{summary['provider']}`",
        f"- Model: `{summary['model']}`",
        f"- Live model calls: `{summary['live_model_calls']}`",
        f"- Candidate count: {len(summary['generation'].get('frontier_candidates', []))}",
        f"- Selected for next budget: `{summary['critique'].get('selected_for_next_budget')}`",
        "",
        "## Interpretation",
        "",
        summary["interpretation"],
        "",
        "## Ranked Candidates",
        "",
    ]
    ranks = {item["id"]: item for item in summary["critique"].get("ranking", [])}
    for candidate in summary["generation"].get("frontier_candidates", []):
        rank = ranks.get(candidate["id"], {})
        lines.extend(
            [
                f"### {candidate['id']}: {candidate['title']}",
                "",
                f"- Overall score: {rank.get('overall_score', 'n/a')}",
                f"- Evidence gain: {rank.get('evidence_gain', 'n/a')}",
                f"- Benchmark fit: {rank.get('benchmark_fit', 'n/a')}",
                f"- Human-taste visibility: {rank.get('human_taste_visibility', 'n/a')}",
                f"- Cost risk: {rank.get('cost_risk', 'n/a')}",
                f"- Core hypothesis: {candidate['core_hypothesis']}",
                f"- Minimal experiment: {candidate['minimal_experiment']}",
                f"- Benchmark/evaluator: {candidate['benchmark_or_evaluator']}",
                f"- Human taste role: {candidate['human_taste_role']}",
                f"- Main risk: {candidate['main_risk']}",
                f"- Failure value: {candidate['failure_value']}",
                f"- Critique: {rank.get('reason', 'n/a')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            summary["critique"].get("claim_boundary", "Not supplied."),
            "",
            "This artifact supports the existence of a live hypothesis-frontier",
            "generation and critique front end. It does not show that the selected",
            "candidate improves downstream benchmark or paper-quality outcomes.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"hypothesis_frontier_smoke_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--max-tokens", type=int, default=1800)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    out_dir = Path(args.output_dir) if args.output_dir else DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    generation_messages = [
        {"role": "system", "content": "You generate rigorous, testable scientific research hypotheses as strict JSON."},
        {"role": "user", "content": _generation_prompt()},
    ]
    generation_response = _call_monica(args.model, generation_messages, args.max_tokens, args.temperature)
    generation_text = _message_text(generation_response)
    generation = _extract_json_object(generation_text)

    critique_messages = [
        {"role": "system", "content": "You critique research plans with conservative evidence discipline as strict JSON."},
        {"role": "user", "content": _critique_prompt(generation)},
    ]
    critique_response = _call_monica(args.model, critique_messages, args.max_tokens, 0.1)
    critique_text = _message_text(critique_response)
    critique = _extract_json_object(critique_text)

    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "provider": "Monica OpenAI-compatible API",
        "model": args.model,
        "live_model_calls": 2,
        "generation_latency_seconds": generation_response.get("_latency_seconds"),
        "critique_latency_seconds": critique_response.get("_latency_seconds"),
        "generation": generation,
        "critique": critique,
        "interpretation": (
            "Live AI Co-Scientist-style generate-critique-rank smoke for IGRE. "
            "This is hypothesis-frontier evidence and a protocol check, not a "
            "performance result or a human-selection result."
        ),
    }

    (out_dir / "generation_prompt.txt").write_text(generation_messages[-1]["content"], encoding="utf-8")
    (out_dir / "critique_prompt.txt").write_text(critique_messages[-1]["content"], encoding="utf-8")
    (out_dir / "generation_raw_response.txt").write_text(generation_text, encoding="utf-8")
    (out_dir / "critique_raw_response.txt").write_text(critique_text, encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")

    print(json.dumps({"run_id": args.run_id, "output_dir": str(out_dir.relative_to(ROOT)), "selected": critique.get("selected_for_next_budget")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
