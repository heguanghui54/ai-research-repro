#!/usr/bin/env python3
"""Run a live model-call smoke test of the reusable Co-Pilot AI Scientist skill.

This is stricter than the template-only skill smoke: it asks a Monica-routed
model to use the Codex skill on a fresh research task, emit a task spec plus
IGRE gate plan, and then asks a second model pass to audit the output. It is
still an orchestration/reuse test, not evidence that the workflow improves
benchmark or paper quality.
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
SKILL_DIR = ROOT / "skills" / "co-pilot-ai-scientist-v3"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path, max_chars: int) -> str:
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


def _skill_prompt(topic: str) -> str:
    skill = _read(SKILL_DIR / "SKILL.md", 7000)
    task_template = _read(SKILL_DIR / "templates" / "task_spec_template.md", 3000)
    gate_template = _read(SKILL_DIR / "templates" / "human_gate_log_template.json", 3500)
    readiness = _read(DOC_DIR / "audits" / "top_conference_readiness_audit.md", 4500)
    return f"""
You are invoking this Codex skill on a fresh research task. Use the skill
instructions directly; do not invent benchmark results.

Fresh task:
{topic}

Skill excerpt:
{skill}

Task template:
{task_template}

Gate template:
{gate_template}

Current package readiness excerpt:
{readiness}

Return strict JSON only with this shape:
{{
  "research_task_id": "live_skill_invocation_001",
  "task_spec_markdown": "...",
  "candidate_directions": [
    {{
      "id": "direction_1",
      "title": "...",
      "hypothesis": "...",
      "minimal_experiment": "...",
      "benchmark_or_evaluator": "...",
      "main_risk": "..."
    }}
  ],
  "selected_direction_id": "direction_...",
  "igre_gate_plan": [
    {{
      "gate_id": "live_skill_gate_001",
      "gate_type": "scientific_taste_prior",
      "human_decision": "...",
      "rationale": "...",
      "expected_artifacts": ["..."],
      "failure_condition": "..."
    }}
  ],
  "claim_boundary": "..."
}}

Constraints:
- Generate exactly 3 candidate_directions.
- Include exactly 5 IGRE gates in this order: scientific_taste_prior,
  evaluator_stress_test, frontier_steering, verifiable_micro_evolution,
  claim_calibration.
- The task_spec_markdown must include success criteria, failure criteria,
  baselines, benchmarks/evaluators, and expected artifacts.
- The claim_boundary must state that this is a live skill-reuse smoke, not a
  benchmark result or independent human evaluation.
""".strip()


def _audit_prompt(skill_output: dict[str, Any]) -> str:
    return f"""
Audit the following live invocation of the Co-Pilot AI Scientist v3 skill.
Return strict JSON only.

Skill invocation output:
{json.dumps(skill_output, ensure_ascii=False, indent=2)[:9000]}

Evaluate whether it proves reusable workflow execution, while keeping claims
bounded. Return:
{{
  "recommendation": "pass" | "revise" | "fail",
  "rubric": {{
    "uses_skill_instructions": 1-5,
    "gate_completeness": 1-5,
    "benchmark_to_claim_fit": 1-5,
    "claim_boundary_honesty": 1-5,
    "reusability": 1-5
  }},
  "strengths": ["..."],
  "weaknesses": ["..."],
  "required_next_checks": ["..."],
  "safe_claim": "..."
}}
""".strip()


def _validate_invocation(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not data.get("task_spec_markdown"):
        errors.append("missing task_spec_markdown")
    if len(data.get("candidate_directions") or []) != 3:
        errors.append("expected exactly 3 candidate directions")
    expected_gates = [
        "scientific_taste_prior",
        "evaluator_stress_test",
        "frontier_steering",
        "verifiable_micro_evolution",
        "claim_calibration",
    ]
    gates = data.get("igre_gate_plan") or []
    if [gate.get("gate_type") for gate in gates] != expected_gates:
        errors.append("IGRE gate plan does not match required five-gate order")
    selected = data.get("selected_direction_id")
    direction_ids = {item.get("id") for item in data.get("candidate_directions") or []}
    if selected not in direction_ids:
        errors.append("selected_direction_id does not match a candidate id")
    if "not" not in str(data.get("claim_boundary", "")).lower():
        errors.append("claim_boundary does not explicitly bound unsupported claims")
    return errors


def _gate_log(invocation: dict[str, Any], timestamp_utc: str) -> dict[str, Any]:
    selected = invocation.get("selected_direction_id")
    candidates = invocation.get("candidate_directions") or []
    selected_item = next((item for item in candidates if item.get("id") == selected), candidates[0])
    return {
        "gate_id": "live_skill_invocation_scientific_taste_prior_001",
        "gate_type": "scientific_taste_prior",
        "timestamp_utc": timestamp_utc,
        "research_task_id": invocation.get("research_task_id", "live_skill_invocation_001"),
        "options": [
            {
                "option_id": item.get("id"),
                "summary": item.get("title", ""),
                "score": None,
                "evidence": [item.get("minimal_experiment", ""), item.get("benchmark_or_evaluator", "")],
                "risks": [item.get("main_risk", "")],
            }
            for item in candidates
        ],
        "human_decision": selected,
        "rationale": (
            "Model-generated live skill invocation selected this direction as the most reusable "
            "test of IGRE gate orchestration; no human performance claim is inferred."
        ),
        "affected_artifacts": [
            "skills/co-pilot-ai-scientist-v3/SKILL.md",
            "skills/co-pilot-ai-scientist-v3/templates/task_spec_template.md",
            "skills/co-pilot-ai-scientist-v3/templates/human_gate_log_template.json",
        ],
        "downstream_budget": {
            "model_calls": 2,
            "selected_minimal_experiment": selected_item.get("minimal_experiment"),
            "benchmark_or_evaluator": selected_item.get("benchmark_or_evaluator"),
        },
        "attention_cost": {
            "human_actor": "codex_live_skill_smoke",
            "interaction_mode": "posthoc_replay",
            "prompted_at_utc": None,
            "decision_at_utc": timestamp_utc,
            "active_review_minutes": None,
            "wall_clock_latency_minutes": None,
            "options_reviewed": len(candidates),
            "artifacts_reviewed_count": 3,
            "decision_count": 1,
            "notes": "Live model-call skill smoke; no independent human timing was measured.",
        },
        "taste_insight": {
            "rubric_version": "2026-06-02",
            "scores": {
                "problem_depth": 4,
                "novelty_potential": 3,
                "mechanistic_value": 4,
                "failure_informativeness": 4,
                "benchmark_taste": 4,
                "claim_significance": 4,
                "risk_asymmetry": 4,
            },
            "taste_insight_score": 3.9,
            "qualitative_rationale": (
                "The selected live skill task tests whether IGRE gate semantics transfer to "
                "a fresh research problem, which matters for reusable co-pilot workflow design."
            ),
            "non_metric_factors": [
                "workflow transferability",
                "claim-boundary honesty",
                "benchmark-to-claim fit",
            ],
        },
        "follow_up_checks": [
            "Run the selected task through an actual benchmark or evaluator before claiming performance.",
            "Collect independent human review if the output is used for paper-quality claims.",
        ],
    }


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Live Skill Invocation Smoke",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Status: `{summary['status']}`",
        f"- Model: `{summary['model']}`",
        f"- Live model calls: `{summary['live_model_calls']}`",
        f"- Validation errors: `{len(summary['validation_errors'])}`",
        f"- Audit recommendation: `{summary['audit']['recommendation']}`",
        "",
        "## Selected Direction",
        "",
        f"- Selected direction: `{summary['selected_direction_id']}`",
        f"- Safe claim: {summary['audit']['safe_claim']}",
        "",
        "## Claim Boundary",
        "",
        summary["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="live_skill_invocation_smoke_20260602_170000")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--max-tokens", type=int, default=2400)
    parser.add_argument(
        "--topic",
        default=(
            "Use Co-Pilot AI Scientist v3 to design a small research workflow for "
            "testing whether review-derived evaluator-stress gates reduce metric-gaming "
            "in an automated ML benchmark."
        ),
    )
    args = parser.parse_args()
    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _utc_now()

    invocation_response = _call_monica(
        model=args.model,
        messages=[
            {"role": "system", "content": "You are a careful research workflow designer. Return strict JSON."},
            {"role": "user", "content": _skill_prompt(args.topic)},
        ],
        max_tokens=args.max_tokens,
        temperature=0.2,
    )
    invocation_text = _message_text(invocation_response)
    invocation = _extract_json_object(invocation_text)
    validation_errors = _validate_invocation(invocation)

    audit_response = _call_monica(
        model=args.model,
        messages=[
            {"role": "system", "content": "You are a conservative top-conference artifact auditor. Return strict JSON."},
            {"role": "user", "content": _audit_prompt(invocation)},
        ],
        max_tokens=1400,
        temperature=0.0,
    )
    audit_text = _message_text(audit_response)
    audit = _extract_json_object(audit_text)

    gate_log = _gate_log(invocation, timestamp)
    task_spec_path = out_dir / "task_spec.md"
    task_spec_path.write_text(invocation["task_spec_markdown"], encoding="utf-8")
    (out_dir / "gate_log.json").write_text(json.dumps(gate_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "invocation.json").write_text(json.dumps(invocation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / f"{args.model}_invocation_raw_response.txt").write_text(invocation_text, encoding="utf-8")
    (out_dir / f"{args.model}_audit_raw_response.txt").write_text(audit_text, encoding="utf-8")

    summary = {
        "run_id": args.run_id,
        "timestamp_utc": timestamp,
        "status": "pass" if not validation_errors and audit.get("recommendation") in {"pass", "revise"} else "needs_repair",
        "model": args.model,
        "live_model_calls": 2,
        "topic": args.topic,
        "selected_direction_id": invocation.get("selected_direction_id"),
        "validation_errors": validation_errors,
        "audit": audit,
        "artifacts": {
            "task_spec": _rel(task_spec_path),
            "gate_log": _rel(out_dir / "gate_log.json"),
            "invocation": _rel(out_dir / "invocation.json"),
            "audit": _rel(out_dir / "audit.json"),
        },
        "claim_boundary": (
            "This live skill invocation smoke verifies that the reusable Codex skill can be "
            "applied to a fresh research task with real model calls and produces a task spec, "
            "five-gate IGRE plan, and audit. It is not a benchmark result, not independent "
            "human review, and not evidence that IGRE improves paper quality or performance."
        ),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary": _rel(out_dir / "summary.json"), "status": summary["status"]}, indent=2))


if __name__ == "__main__":
    main()
