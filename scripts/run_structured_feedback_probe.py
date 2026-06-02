#!/usr/bin/env python3
"""Compare informal feedback with IGRE-structured feedback on one manuscript.

This is a downstream measurement probe for the hypothesis-frontier smoke. It
does not claim that structured human feedback generally improves papers; it
archives a same-manuscript, same-model comparison that can be repeated or
replaced with human expert review.
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
DEFAULT_MANUSCRIPT = (
    DOC_DIR
    / "experiments"
    / "online_full_gate_smoke_20260602_013612"
    / "online_manuscript"
    / "co_pilot_online_full_gate_manuscript.md"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path, max_chars: int | None = None) -> str:
    text = path.read_text(encoding="utf-8")
    return text if max_chars is None else text[:max_chars]


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
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("model response does not contain a JSON object")
    return json.loads(stripped[start : end + 1])


def _informal_feedback_prompt(manuscript: str) -> str:
    return f"""
You are giving quick free-form feedback on a research manuscript draft.
Respond like a helpful research collaborator. Do not use a fixed rubric.
Focus on what should be improved before submission.

Manuscript:
```markdown
{manuscript}
```
""".strip()


def _structured_feedback_prompt(manuscript: str, taste_rubric: str, claim_matrix: str) -> str:
    return f"""
You are the IGRE (Insight-Gated Research Evolution) structured feedback gate.
Use the protocol below to produce feedback that makes human scientific taste and
claim calibration explicit rather than treating the human as generic approval.

Required feedback sections:
1. Taste prior: what is scientifically interesting, elegant, or high-tail here?
2. Attention allocation: what should the next limited budget inspect first?
3. Claim calibration: which claims are supported, overclaimed, or missing?
4. Method distinctness: how can IGRE avoid looking like a mashup of prior agents?
5. Reproducibility pressure: what evidence or artifacts must become inspectable?
6. Failure value: what negative result would still teach something?
7. Revision instructions: concrete edits ordered by expected evidence gain.

Taste/insight rubric excerpt:
```markdown
{taste_rubric}
```

Benchmark-to-claim matrix excerpt:
```markdown
{claim_matrix}
```

Manuscript:
```markdown
{manuscript}
```
""".strip()


def _revision_prompt(manuscript: str, feedback: str, mode: str) -> str:
    return f"""
Revise the manuscript using the supplied {mode} feedback.

Constraints:
- Do not invent experiments, citations, metrics, or user studies.
- Preserve the same evidence base.
- Tighten unsupported claims.
- Keep the revised manuscript concise but complete.
- Make limitations explicit.

Feedback:
```markdown
{feedback}
```

Original manuscript:
```markdown
{manuscript}
```

Return only the revised manuscript in Markdown.
""".strip()


def _score_prompt(informal_revision: str, structured_revision: str) -> str:
    return f"""
You are a strict paper-quality auditor. Compare two revisions of the same base
manuscript. The revisions were produced with the same model and evidence base;
only the feedback mode differs.

Score only the text supplied here. Do not infer missing experiments. Return
strict JSON only with this schema:
{{
  "recommendation": "informal" | "structured" | "tie",
  "scores": {{
    "informal": {{
      "clarity": 1-5,
      "reproducibility": 1-5,
      "claim_calibration": 1-5,
      "evidence_grounding": 1-5,
      "method_distinctness": 1-5,
      "limitation_honesty": 1-5,
      "novelty_preservation": 1-5,
      "overall": 1-5
    }},
    "structured": {{
      "clarity": 1-5,
      "reproducibility": 1-5,
      "claim_calibration": 1-5,
      "evidence_grounding": 1-5,
      "method_distinctness": 1-5,
      "limitation_honesty": 1-5,
      "novelty_preservation": 1-5,
      "overall": 1-5
    }}
  }},
  "rationale": "short paragraph",
  "structured_feedback_helped": ["dimension 1", "dimension 2"],
  "structured_feedback_hurt": ["dimension 1"],
  "required_next_evidence": ["item 1", "item 2", "item 3"]
}}

Informal-feedback revision:
```markdown
{informal_revision}
```

Structured-feedback revision:
```markdown
{structured_revision}
```
""".strip()


def _write(path: Path, text: str) -> str:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_structured_feedback_probe"
    manifest["structured_feedback_probe"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "base_manuscript": summary["base_manuscript"],
        "recommendation": summary["score"].get("recommendation"),
        "scope_note": summary["scope_note"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _markdown(summary: dict[str, Any]) -> str:
    score = summary["score"]
    scores = score.get("scores", {})
    informal = scores.get("informal", {}) if isinstance(scores, dict) else {}
    structured = scores.get("structured", {}) if isinstance(scores, dict) else {}
    lines = [
        "# Structured Feedback Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Provider: `{summary['provider']}`",
        f"- Model: `{summary['model']}`",
        f"- Base manuscript: `{summary['base_manuscript']}`",
        f"- Recommendation: `{score.get('recommendation', 'unparsed')}`",
        f"- Informal overall: `{informal.get('overall', 'n/a')}`",
        f"- Structured overall: `{structured.get('overall', 'n/a')}`",
        "",
        "## Scope",
        "",
        summary["scope_note"],
        "",
        "## Interpretation",
        "",
        summary["interpretation"],
        "",
        "## Score Table",
        "",
        "| Dimension | Informal | Structured |",
        "| --- | ---: | ---: |",
    ]
    for key in [
        "clarity",
        "reproducibility",
        "claim_calibration",
        "evidence_grounding",
        "method_distinctness",
        "limitation_honesty",
        "novelty_preservation",
        "overall",
    ]:
        lines.append(f"| {key} | {informal.get(key, 'n/a')} | {structured.get(key, 'n/a')} |")
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
            "This probe is model-routed and same-manuscript only. It should be used",
            "as measurement-readiness evidence, not as a replacement for independent",
            "human expert review or multi-task matched-budget evaluation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"structured_feedback_probe_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--base-manuscript", default=str(DEFAULT_MANUSCRIPT))
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--max-feedback-tokens", type=int, default=1400)
    parser.add_argument("--max-revision-tokens", type=int, default=2600)
    parser.add_argument("--max-score-tokens", type=int, default=1400)
    args = parser.parse_args()

    if not os.environ.get("MONICA_API_KEY"):
        raise SystemExit("MONICA_API_KEY is required. Source the private Codex env before running.")

    base_path = Path(args.base_manuscript)
    if not base_path.is_absolute():
        base_path = ROOT / base_path
    out_dir = Path(args.output_dir) if args.output_dir else DOC_DIR / "experiments" / args.run_id
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    manuscript = _read(base_path, 12000)
    taste_rubric = _read(DOC_DIR / "taste_insight_rubric.md", 4000)
    claim_matrix = _read(DOC_DIR / "benchmark_claim_matrix.md", 4000)

    informal_prompt = _informal_feedback_prompt(manuscript)
    structured_prompt = _structured_feedback_prompt(manuscript, taste_rubric, claim_matrix)

    common_system = {
        "role": "system",
        "content": "You are a careful research-writing collaborator. You do not invent evidence.",
    }
    informal_response = _call_monica(
        model=args.model,
        messages=[common_system, {"role": "user", "content": informal_prompt}],
        max_tokens=args.max_feedback_tokens,
        temperature=0.2,
    )
    structured_response = _call_monica(
        model=args.model,
        messages=[common_system, {"role": "user", "content": structured_prompt}],
        max_tokens=args.max_feedback_tokens,
        temperature=0.2,
    )
    informal_feedback = _message_text(informal_response)
    structured_feedback = _message_text(structured_response)

    informal_revision_prompt = _revision_prompt(manuscript, informal_feedback, "informal")
    structured_revision_prompt = _revision_prompt(manuscript, structured_feedback, "IGRE-structured")
    informal_revision_response = _call_monica(
        model=args.model,
        messages=[common_system, {"role": "user", "content": informal_revision_prompt}],
        max_tokens=args.max_revision_tokens,
        temperature=0.15,
    )
    structured_revision_response = _call_monica(
        model=args.model,
        messages=[common_system, {"role": "user", "content": structured_revision_prompt}],
        max_tokens=args.max_revision_tokens,
        temperature=0.15,
    )
    informal_revision = _message_text(informal_revision_response)
    structured_revision = _message_text(structured_revision_response)

    scoring_prompt = _score_prompt(informal_revision, structured_revision)
    scoring_response = _call_monica(
        model=args.model,
        messages=[
            {
                "role": "system",
                "content": "You are a strict paper-quality scoring auditor. Return valid JSON only.",
            },
            {"role": "user", "content": scoring_prompt},
        ],
        max_tokens=args.max_score_tokens,
        temperature=0.05,
    )
    scoring_text = _message_text(scoring_response)
    score = _extract_json_object(scoring_text)

    paths: list[str] = []
    paths.append(_write(out_dir / "base_manuscript_excerpt.md", manuscript))
    paths.append(_write(out_dir / "informal_feedback_prompt.txt", informal_prompt))
    paths.append(_write(out_dir / "structured_feedback_prompt.txt", structured_prompt))
    paths.append(_write(out_dir / "informal_feedback.md", informal_feedback))
    paths.append(_write(out_dir / "structured_feedback.md", structured_feedback))
    paths.append(_write(out_dir / "informal_revision_prompt.txt", informal_revision_prompt))
    paths.append(_write(out_dir / "structured_revision_prompt.txt", structured_revision_prompt))
    paths.append(_write(out_dir / "informal_revision.md", informal_revision))
    paths.append(_write(out_dir / "structured_revision.md", structured_revision))
    paths.append(_write(out_dir / "scoring_prompt.txt", scoring_prompt))
    paths.append(_write(out_dir / "scoring_raw_response.txt", scoring_text))
    paths.append(
        _write(
            out_dir / "model_responses.json",
            json.dumps(
                {
                    "informal_feedback": informal_response,
                    "structured_feedback": structured_response,
                    "informal_revision": informal_revision_response,
                    "structured_revision": structured_revision_response,
                    "scoring": scoring_response,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
    )

    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "structured_feedback_measurement_probe",
        "provider": "Monica OpenAI-compatible API",
        "model": args.model,
        "live_model_calls": 5,
        "base_manuscript": _rel(base_path),
        "summary_path": _rel(out_dir / "summary.json"),
        "scope_note": (
            "Same-base-manuscript, same-model probe comparing informal feedback "
            "against IGRE-structured feedback. This is measurement-readiness "
            "evidence only, not independent human expert review."
        ),
        "interpretation": (
            "The probe operationalizes frontier_004 from the hypothesis-frontier "
            "smoke by turning structured feedback into a downstream revision and "
            "scoring test. It checks whether the IGRE feedback format can make "
            "claim calibration, method distinctness, and reproducibility pressure "
            "visible in generated revisions."
        ),
        "score": score,
        "artifacts": paths,
    }
    paths.append(_write(out_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2)))
    paths.append(_write(out_dir / "README.md", _markdown(summary)))
    summary["artifacts"] = paths
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _update_manifest(paths + ["scripts/run_structured_feedback_probe.py"], summary)
    print(json.dumps({"summary": summary["summary_path"], "recommendation": score.get("recommendation")}, indent=2))


if __name__ == "__main__":
    main()
