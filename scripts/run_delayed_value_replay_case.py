#!/usr/bin/env python3
"""Execute one delayed-value replay case across four preregistered conditions."""

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
SPEC_RUN = DOC_DIR / "experiments" / "delayed_value_replay_specs_20260602_234500"
DEFAULT_CASE_ID = "paper_105_review_1"
CONDITIONS = [
    "paper_only",
    "raw_review_guided",
    "six_gate_hybrid_guided",
    "shuffled_review_control",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    last_error = None
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


def _generation_prompt(case_id: str, spec: dict[str, Any], prompts: dict[str, str]) -> str:
    return f"""
You are executing a preregistered Temporal Frontier Replay case for Co-Pilot AI Scientist v3.

Case ID: {case_id}
Title: {spec['title']}
Domain: {spec['domain']}
Replay question: {spec['replay_question']}

You must generate one mini-paper research artifact for each condition below.
Treat condition separation as strict experimental control. Do not leak the raw
review into paper_only or shuffled_review_control beyond what those prompts allow.

Preregistered replay spec:
{json.dumps(spec, ensure_ascii=False, indent=2)}

Condition prompts:
{json.dumps(prompts, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "case_id": "{case_id}",
  "artifacts": {{
    "paper_only": {{
      "hypothesis": "...",
      "method": "...",
      "experiment_plan": "...",
      "ablation_or_stress_test": "...",
      "expected_evidence": "...",
      "failure_modes": "...",
      "claim_boundary": "...",
      "mini_paper": "300-450 words"
    }},
    "raw_review_guided": {{
      "hypothesis": "...",
      "review_signal_used": ["..."],
      "method": "...",
      "experiment_plan": "...",
      "ablation_or_stress_test": "...",
      "expected_evidence": "...",
      "failure_modes": "...",
      "claim_boundary": "...",
      "mini_paper": "300-450 words"
    }},
    "six_gate_hybrid_guided": {{
      "hypothesis": "...",
      "gate_actions": {{
        "scientific_taste_prior": "...",
        "evaluator_stress_test": "...",
        "frontier_steering": "...",
        "verifiable_micro_evolution": "...",
        "structured_feedback": "...",
        "claim_calibration": "..."
      }},
      "method": "...",
      "experiment_plan": "...",
      "ablation_or_stress_test": "...",
      "expected_evidence": "...",
      "failure_modes": "...",
      "claim_boundary": "...",
      "mini_paper": "300-450 words"
    }},
    "shuffled_review_control": {{
      "hypothesis": "...",
      "control_signal_used": ["..."],
      "method": "...",
      "experiment_plan": "...",
      "ablation_or_stress_test": "...",
      "expected_evidence": "...",
      "failure_modes": "...",
      "claim_boundary": "...",
      "mini_paper": "300-450 words"
    }}
  }},
  "generation_claim_boundary": "No completed benchmark result is claimed."
}}
""".strip()


def _scoring_prompt(case_id: str, spec: dict[str, Any], generated: dict[str, Any]) -> str:
    return f"""
You are a conservative Temporal Frontier Replay judge.

Score the four generated artifacts for the same delayed-value replay case.
Use only the text below. Do not infer completed experiments. The goal is to
judge research-plan quality and future-frontier alignment, not acceptance.

Case ID: {case_id}
Title: {spec['title']}
Positive delayed-value rule:
{json.dumps(spec['positive_delayed_value_rule'], ensure_ascii=False, indent=2)}

Short-term metrics:
{json.dumps(spec['short_term_metrics'], ensure_ascii=False, indent=2)}

Frontier metrics:
{json.dumps(spec['frontier_metrics'], ensure_ascii=False, indent=2)}

Generated artifacts:
{json.dumps(generated, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "case_id": "{case_id}",
  "per_condition": {{
    "paper_only": {{
      "short_term_score": 1-5,
      "frontier_alignment_score": 1-5,
      "actionability_score": 1-5,
      "specificity_score": 1-5,
      "claim_calibration_score": 1-5,
      "overall": 1-5,
      "rationale": "..."
    }},
    "raw_review_guided": {{ "... same fields ...": "" }},
    "six_gate_hybrid_guided": {{ "... same fields ...": "" }},
    "shuffled_review_control": {{ "... same fields ...": "" }}
  }},
  "winner_short_term": "paper_only|raw_review_guided|six_gate_hybrid_guided|shuffled_review_control|tie",
  "winner_frontier": "paper_only|raw_review_guided|six_gate_hybrid_guided|shuffled_review_control|tie",
  "delayed_value_label": "positive|negative|mixed_or_inconclusive",
  "delayed_value_rationale": "...",
  "best_review_signal": "raw_review_guided|six_gate_hybrid_guided|none",
  "failure_modes_observed": ["..."],
  "claim_boundary": "..."
}}
""".strip()


def _normalize_scores(scoring: dict[str, Any]) -> dict[str, Any]:
    per = scoring.get("per_condition", {})
    normalized: dict[str, Any] = {}
    for condition in CONDITIONS:
        row = per.get(condition) or {}
        out = {}
        for key in [
            "short_term_score",
            "frontier_alignment_score",
            "actionability_score",
            "specificity_score",
            "claim_calibration_score",
            "overall",
        ]:
            value = row.get(key)
            if not isinstance(value, (int, float)):
                value = 0
            out[key] = float(value)
        out["rationale"] = row.get("rationale", "")
        normalized[condition] = out
    scoring["per_condition"] = normalized

    def _best(metric: str) -> str:
        values = {condition: normalized[condition][metric] for condition in CONDITIONS}
        best_value = max(values.values())
        winners = [condition for condition, value in values.items() if value == best_value]
        return winners[0] if len(winners) == 1 else "tie"

    scoring["winner_short_term"] = _best("short_term_score")
    scoring["winner_frontier"] = _best("frontier_alignment_score")
    paper = normalized["paper_only"]
    shuffled = normalized["shuffled_review_control"]
    guided_candidates = ["raw_review_guided", "six_gate_hybrid_guided"]
    positives = []
    for condition in guided_candidates:
        row = normalized[condition]
        if (
            row["short_term_score"] < paper["short_term_score"]
            and row["frontier_alignment_score"] > paper["frontier_alignment_score"]
            and row["frontier_alignment_score"] > shuffled["frontier_alignment_score"]
            and row["actionability_score"] >= 4
            and row["specificity_score"] >= 4
        ):
            positives.append(condition)
    model_delayed_value_label = scoring.get("delayed_value_label")
    scoring["model_delayed_value_label"] = model_delayed_value_label
    if positives:
        scoring["delayed_value_label"] = "positive"
        scoring["best_review_signal"] = positives[0]
        scoring["deterministic_label_note"] = "strict preregistered delayed-value rule satisfied"
    else:
        scoring["delayed_value_label"] = "mixed_or_inconclusive"
        scoring["best_review_signal"] = "none"
        scoring["deterministic_label_note"] = (
            "strict preregistered delayed-value rule not satisfied; guided conditions "
            "did not have lower short-term score than paper_only while beating paper_only "
            "and shuffled_control on frontier alignment"
        )
    return scoring


def _markdown(summary: dict[str, Any]) -> str:
    scoring = summary["scoring"]
    lines = [
        "# Delayed-Value Replay Case Execution",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Case ID: `{summary['case_id']}`",
        f"- Title: `{summary['title']}`",
        f"- Generation model: `{summary['generation_model']}`",
        f"- Judge model: `{summary['judge_model']}`",
        f"- Live model calls: `{summary['live_model_calls']}`",
        f"- Winner short-term: `{scoring.get('winner_short_term')}`",
        f"- Winner frontier: `{scoring.get('winner_frontier')}`",
        f"- Delayed-value label: `{scoring.get('delayed_value_label')}`",
        "",
        "## Scores",
        "",
        "| Condition | Short-term | Frontier | Actionability | Specificity | Claim calibration | Overall |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, row in scoring.get("per_condition", {}).items():
        lines.append(
            f"| `{condition}` | {row.get('short_term_score')} | {row.get('frontier_alignment_score')} | "
            f"{row.get('actionability_score')} | {row.get('specificity_score')} | "
            f"{row.get('claim_calibration_score')} | {row.get('overall')} |"
        )
    lines.extend(["", "## Delayed-Value Rationale", "", scoring.get("delayed_value_rationale", ""), ""])
    lines.extend(["## Condition Rationales", ""])
    for condition, row in scoring.get("per_condition", {}).items():
        lines.append(f"- `{condition}`: {row.get('rationale', '')}")
    lines.extend(["", "## Claim Boundary", "", summary["claim_boundary"], ""])
    return "\n".join(lines)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["delayed_value_replay_case_execution"] = {
        "run_id": summary["run_id"],
        "case_id": summary["case_id"],
        "summary": summary["summary_path"],
        "status": summary["status"],
        "generation_model": summary["generation_model"],
        "judge_model": summary["judge_model"],
        "delayed_value_label": summary["scoring"].get("delayed_value_label"),
        "winner_frontier": summary["scoring"].get("winner_frontier"),
        "claim_boundary": summary["claim_boundary"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", default=DEFAULT_CASE_ID)
    parser.add_argument("--generation-model", default="gpt-4o-mini")
    parser.add_argument("--judge-model", default="gpt-4o-mini")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--max-tokens", type=int, default=7000)
    parser.add_argument("--no-manifest", action="store_true")
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source ~/.codex/env before running.")

    case_dir = SPEC_RUN / args.case_id
    spec = _load_json(case_dir / "replay_spec.json")
    prompts = {condition: _read(case_dir / f"{condition}_prompt.txt") for condition in CONDITIONS}
    run_id = args.run_id or f"delayed_value_replay_case_{args.case_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    out_dir = DOC_DIR / "experiments" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []

    generation_prompt = _generation_prompt(args.case_id, spec, prompts)
    paths.append(_write(out_dir / "generation_prompt.txt", generation_prompt))
    generation_response = _call_monica(
        model=args.generation_model,
        messages=[
            {"role": "system", "content": "Return strict JSON. Keep all claims evidence-bound."},
            {"role": "user", "content": generation_prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.25,
    )
    generation_text = _message_text(generation_response)
    paths.append(_write(out_dir / "generation_raw_response.txt", generation_text))
    try:
        generated = _extract_json_object(generation_text)
    except Exception as exc:  # noqa: BLE001 - archived as live-model failure evidence.
        summary = {
            "run_id": run_id,
            "timestamp_utc": _utc_now(),
            "status": "failed_generation_json_parse",
            "case_id": args.case_id,
            "title": spec["title"],
            "source_spec": _rel(case_dir / "replay_spec.json"),
            "generation_model": args.generation_model,
            "judge_model": args.judge_model,
            "live_model_calls": 1,
            "generation_latency_seconds": generation_response.get("_latency_seconds"),
            "generated": {},
            "scoring": {},
            "parse_error": repr(exc),
            "claim_boundary": (
                "This failed live replay is archived as model-output robustness evidence. "
                "No replay score, benchmark result, or delayed-value claim is made."
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
        if not args.no_manifest:
            _update_manifest(paths + ["scripts/run_delayed_value_replay_case.py"], summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    paths.append(_write(out_dir / "generated_artifacts.json", json.dumps(generated, ensure_ascii=False, indent=2)))

    scoring_prompt = _scoring_prompt(args.case_id, spec, generated)
    paths.append(_write(out_dir / "scoring_prompt.txt", scoring_prompt))
    scoring_response = _call_monica(
        model=args.judge_model,
        messages=[
            {"role": "system", "content": "Return strict JSON. Score conservatively."},
            {"role": "user", "content": scoring_prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.05,
    )
    scoring_text = _message_text(scoring_response)
    paths.append(_write(out_dir / "scoring_raw_response.txt", scoring_text))
    try:
        scoring = _normalize_scores(_extract_json_object(scoring_text))
    except Exception as exc:  # noqa: BLE001 - archived as live-model failure evidence.
        summary = {
            "run_id": run_id,
            "timestamp_utc": _utc_now(),
            "status": "failed_scoring_json_parse",
            "case_id": args.case_id,
            "title": spec["title"],
            "source_spec": _rel(case_dir / "replay_spec.json"),
            "generation_model": args.generation_model,
            "judge_model": args.judge_model,
            "live_model_calls": 2,
            "generation_latency_seconds": generation_response.get("_latency_seconds"),
            "scoring_latency_seconds": scoring_response.get("_latency_seconds"),
            "generated": generated,
            "scoring": {},
            "parse_error": repr(exc),
            "claim_boundary": (
                "This failed live replay is archived as judge-output robustness evidence. "
                "Generated artifacts exist, but no replay score, benchmark result, or "
                "delayed-value claim is made."
            ),
        }
        for condition, artifact in (generated.get("artifacts") or {}).items():
            paths.append(_write(out_dir / f"{condition}_artifact.md", artifact.get("mini_paper", "")))
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
        if not args.no_manifest:
            _update_manifest(paths + ["scripts/run_delayed_value_replay_case.py"], summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        raise SystemExit(2)

    summary: dict[str, Any] = {
        "run_id": run_id,
        "timestamp_utc": _utc_now(),
        "status": "executed_delayed_value_replay_case",
        "case_id": args.case_id,
        "title": spec["title"],
        "source_spec": _rel(case_dir / "replay_spec.json"),
        "generation_model": args.generation_model,
        "judge_model": args.judge_model,
        "live_model_calls": 2,
        "generation_latency_seconds": generation_response.get("_latency_seconds"),
        "scoring_latency_seconds": scoring_response.get("_latency_seconds"),
        "generated": generated,
        "scoring": scoring,
        "claim_boundary": (
            "This is one live model-generated four-condition mini-paper replay. It scores "
            "research-plan artifacts only; it does not rerun the original paper benchmarks, "
            "collect human expert ratings, or prove delayed-value review efficacy."
        ),
    }

    paths.append(_write(out_dir / "condition_scores.json", json.dumps(scoring, ensure_ascii=False, indent=2)))
    summary_path = out_dir / "summary.json"
    summary["summary_path"] = _rel(summary_path)
    paths.extend(
        [
            _write(summary_path, json.dumps(summary, ensure_ascii=False, indent=2)),
            _write(out_dir / "README.md", _markdown(summary)),
        ]
    )
    for condition, artifact in (generated.get("artifacts") or {}).items():
        paths.append(_write(out_dir / f"{condition}_artifact.md", artifact.get("mini_paper", "")))
    summary["artifacts_written"] = paths
    _write(summary_path, json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.no_manifest:
        _update_manifest(paths + ["scripts/run_delayed_value_replay_case.py"], summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
