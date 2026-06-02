#!/usr/bin/env python3
"""Mine useful human scientific taste/insight patterns from OpenReview text.

The goal is not to model all peer review. It is to identify which types of
review comments are actionable for a co-pilot automated research workflow and
which IGRE gate each comment type should influence.
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


def _review_cases(limit: int) -> list[dict[str, Any]]:
    rows = _load_json(EXPERT_PROBE_DIR / "sample_rows_compact.json")
    cases: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        snippets = row.get("review_snippets") or []
        if not snippets:
            continue
        cases.append(
            {
                "case_id": f"review_case_{index}",
                "title": row.get("title"),
                "decision": row.get("decision"),
                "mean_score": row.get("mean_score"),
                "abstract_excerpt": (row.get("abstract_excerpt") or "")[:420],
                "review_snippets": [snippet[:550] for snippet in snippets[:2]],
            }
        )
        if len(cases) >= limit:
            break
    return cases


def _taxonomy_prompt(cases: list[dict[str, Any]]) -> str:
    return f"""
You are analyzing real OpenReview comments as human scientific taste and
insight. Not every review comment is equally useful for an automated research
co-pilot. Identify which kinds of review insight are actionable for improving
AI-generated research.

Map useful review insights to IGRE gates:
- scientific_taste_prior: changes which problem/direction is worth pursuing.
- evaluator_stress_test: exposes weak metrics, missing baselines, or metric gaming.
- frontier_steering: suggests which branch to continue or prune.
- verifiable_micro_evolution: identifies machine-gradeable subproblems.
- structured_feedback: improves manuscript clarity, evidence presentation, or reproducibility.
- claim_calibration: weakens unsupported claims or adds limitations.

Review cases:
{json.dumps(cases, ensure_ascii=False, indent=2)}

Return strict JSON only:
{{
  "taxonomy": [
    {{
      "category": "short category name",
      "description": "...",
      "actionability": 1-5,
      "primary_gate": "one IGRE gate",
      "secondary_gates": ["..."],
      "useful_signal": "what this review type tells the agent",
      "failure_if_ignored": "what goes wrong if the agent ignores it",
      "example_review_patterns": ["short paraphrased pattern 1", "pattern 2"]
    }}
  ],
  "most_useful_categories": ["..."],
  "least_useful_or_noisy_categories": ["..."],
  "workflow_rules": [
    {{
      "rule": "...",
      "target_gate": "...",
      "rationale": "..."
    }}
  ],
  "claim_boundary": "short paragraph"
}}
""".strip()


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Review Insight Taxonomy Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Model: `{summary['model']}`",
        f"- Review cases: `{summary['review_case_count']}`",
        f"- Live model calls: `{summary['live_model_calls']}`",
        "",
        "## Scope",
        "",
        summary["scope_note"],
        "",
        "## Taxonomy",
        "",
        "| Category | Actionability | Primary gate | Useful signal |",
        "| --- | ---: | --- | --- |",
    ]
    for item in summary["taxonomy"].get("taxonomy", []):
        lines.append(
            f"| {item.get('category')} | {item.get('actionability')} | "
            f"{item.get('primary_gate')} | {item.get('useful_signal')} |"
        )
    lines.extend(["", "## Most Useful Categories", ""])
    for item in summary["taxonomy"].get("most_useful_categories", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Workflow Rules", ""])
    for rule in summary["taxonomy"].get("workflow_rules", []):
        lines.append(f"- `{rule.get('target_gate')}`: {rule.get('rule')} ({rule.get('rationale')})")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            summary["taxonomy"].get("claim_boundary", ""),
            "",
            "This taxonomy is model-routed and derived from a finite OpenReview",
            "sample. It identifies actionable review patterns for workflow design;",
            "it does not prove that any single category improves final paper quality.",
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
    manifest["status"] = "pilot_package_with_review_insight_taxonomy_probe"
    manifest["review_insight_taxonomy_probe"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "review_case_count": summary["review_case_count"],
        "most_useful_categories": summary["taxonomy"].get("most_useful_categories", []),
        "claim_boundary": "OpenReview-derived actionable-review taxonomy only; not causal proof.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"review_insight_taxonomy_probe_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--review-limit", type=int, default=32)
    parser.add_argument("--max-tokens", type=int, default=5000)
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    cases = _review_cases(args.review_limit)
    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    prompt = _taxonomy_prompt(cases)
    response = _call_monica(
        model=args.model,
        messages=[
            {"role": "system", "content": "Return strict JSON. Extract actionable workflow-design signals."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=args.max_tokens,
        temperature=0.15,
    )
    raw_text = _message_text(response)
    taxonomy = _extract_json_object(raw_text)

    summary: dict[str, Any] = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "review_insight_taxonomy_probe",
        "model": args.model,
        "live_model_calls": 1,
        "review_case_count": len(cases),
        "scope_note": (
            "Finite OpenReview sample used to identify which human review "
            "comments are actionable as scientific taste/insight for IGRE gates."
        ),
        "latency_seconds": response.get("_latency_seconds"),
        "taxonomy": taxonomy,
    }
    paths = [
        _write(out_dir / "review_cases.json", json.dumps(cases, ensure_ascii=False, indent=2)),
        _write(out_dir / "taxonomy_prompt.txt", prompt),
        _write(out_dir / "taxonomy_raw_response.txt", raw_text),
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
    _update_manifest(paths + ["scripts/run_review_insight_taxonomy_probe.py"], summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
