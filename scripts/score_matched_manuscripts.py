#!/usr/bin/env python3
"""Score matched co-pilot and autonomous mini-manuscripts.

This is a narrow paper-quality probe. It does not evaluate a full generated
paper. It only compares same-package mini-manuscripts derived from one
prospective matched-budget package, so the output must be treated as pilot
evidence rather than a top-conference claim.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = (
    ROOT
    / "docs/co_pilot_ai_scientist_v3/experiments/"
    / "prospective_matched_fml_causality_20260602_000001"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _primary_metric(summary: dict[str, Any]) -> float | None:
    value = summary.get("test_result", {}).get("primary_metric")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _write_autonomous_manuscript(package_dir: Path) -> Path:
    manifest = _load_json(package_dir / "prospective_manifest.json")
    autonomous_summary = _load_json(ROOT / manifest["autonomous_baseline"])
    trajectory = _load_json(ROOT / manifest["co_pilot_trajectory"])
    co_pilot_score = trajectory.get("co_pilot_test_metric")
    autonomous_score = _primary_metric(autonomous_summary)
    path = package_dir / "autonomous_manuscript.md"
    text = f"""# Autonomous FML Matched-Budget Pilot Manuscript

Run ID: `{manifest['package_id']}`

## Question

Can an autonomous AI Scientist-v2 run produce a matched-budget baseline on the
same FML-bench task used by the Co-Pilot AI Scientist v3 prospective package?

## Method

This baseline uses `{autonomous_summary.get('benchmark')}`, model
`{autonomous_summary.get('model')}`, provider `{autonomous_summary.get('provider')}`,
and the same two-step budget recorded in the matched package manifest. It does
not include a human frontier-steering gate or taste/attention log.

## Results

| Variant | Validation metric | Test MAE |
| --- | ---: | ---: |
| Autonomous matched baseline | {_fmt(autonomous_summary.get('best_val_metric'))} | {_fmt(autonomous_score)} |
| Co-pilot package comparator | n/a | {_fmt(co_pilot_score)} |

Lower MAE is better. In this package, the autonomous baseline has the lower
test MAE.

## Claim

This baseline supports a negative control for the co-pilot package: under the
same task, model family, tool access, and step budget, the autonomous run does
better on the held-out test metric. It does not evaluate human scientific taste,
attention efficiency, or paper quality; it only supplies a matched benchmark
and manuscript comparator for the current prospective pilot.
"""
    path.write_text(text, encoding="utf-8")
    return path


def _prompt(manuscript_a: str, manuscript_b: str) -> str:
    return f"""You are a strict ML systems paper-quality judge.

Compare two anonymized mini-manuscripts from the same matched-budget pilot.
Score manuscript quality only. Do not reward a manuscript merely because its
reported method has a better benchmark number; reward clear claims, faithful use
of evidence, honest limitations, methodological completeness, and readability.

Return ONLY valid JSON with this schema:
{{
  "recommendation": "A" | "B" | "tie",
  "scores": {{
    "A": {{
      "claim_calibration": 1-5,
      "evidence_use": 1-5,
      "methodological_completeness": 1-5,
      "limitation_honesty": 1-5,
      "clarity": 1-5,
      "overall": 1-5
    }},
    "B": {{
      "claim_calibration": 1-5,
      "evidence_use": 1-5,
      "methodological_completeness": 1-5,
      "limitation_honesty": 1-5,
      "clarity": 1-5,
      "overall": 1-5
    }}
  }},
  "rationale": "short paragraph",
  "required_next_evidence": ["item 1", "item 2", "item 3"]
}}

Manuscript A:
```markdown
{manuscript_a}
```

Manuscript B:
```markdown
{manuscript_b}
```
"""


def _call_model(model: str, prompt: str, max_tokens: int) -> dict[str, Any]:
    base_url = os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1").rstrip("/")
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['MONICA_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You judge paper quality from supplied text only. "
                        "You return valid JSON and do not invent experiments."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
        },
        timeout=180,
    )
    return {
        "model": model,
        "status_code": response.status_code,
        "response": response.json(),
    }


def _content(result: dict[str, Any]) -> str:
    try:
        return result["response"]["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return json.dumps(result["response"], ensure_ascii=False, indent=2)


def _parse_jsonish(content: str) -> dict[str, Any] | None:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Matched Mini-Manuscript Quality Score",
        "",
        "This is a narrow quality probe over two mini-manuscripts from one",
        "prospective matched-budget package. It is not evidence that the full",
        "Co-Pilot AI Scientist v3 system writes better papers.",
        "",
        "## Package",
        "",
        f"- Package: `{summary['package_id']}`",
        f"- Co-pilot manuscript: `{summary['co_pilot_manuscript']}`",
        f"- Autonomous manuscript: `{summary['autonomous_manuscript']}`",
        "",
        "## Aggregate",
        "",
        f"- Successful reviewer calls: {summary['successful_reviews']}/{summary['review_count']}",
        f"- Co-pilot manuscript wins: {summary['co_pilot_wins']}",
        f"- Autonomous manuscript wins: {summary['autonomous_wins']}",
        f"- Ties: {summary['ties']}",
        "",
        "## Reviewer Results",
        "",
        "| Model | Status | Recommendation | A overall | B overall | Interpretation |",
        "| --- | ---: | --- | ---: | ---: | --- |",
    ]
    for review in summary["reviews"]:
        parsed = review.get("parsed")
        recommendation = parsed.get("recommendation") if isinstance(parsed, dict) else "unparsed"
        scores = parsed.get("scores", {}) if isinstance(parsed, dict) else {}
        a_overall = scores.get("A", {}).get("overall") if isinstance(scores, dict) else None
        b_overall = scores.get("B", {}).get("overall") if isinstance(scores, dict) else None
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{review['model']}`",
                    str(review["status_code"]),
                    str(recommendation),
                    str(a_overall if a_overall is not None else "n/a"),
                    str(b_overall if b_overall is not None else "n/a"),
                    review["interpretation"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The manuscripts are intentionally anonymized as A and B during scoring.",
            "In this run, A is the co-pilot package manuscript and B is the matched",
            "autonomous baseline manuscript. The score should be used only as a",
            "measurement-readiness artifact: a future strong claim requires full",
            "manuscripts from complete end-to-end trajectories, multiple tasks, and",
            "independent expert scoring.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", default=str(DEFAULT_PACKAGE))
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gpt-4o-mini", "claude-3-7-sonnet-latest"],
    )
    parser.add_argument("--max-tokens", type=int, default=2200)
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    if not package_dir.is_absolute():
        package_dir = ROOT / package_dir
    manifest = _load_json(package_dir / "prospective_manifest.json")
    co_pilot_manuscript = package_dir / "manuscript.md"
    autonomous_manuscript = _write_autonomous_manuscript(package_dir)

    prompt = _prompt(
        co_pilot_manuscript.read_text(encoding="utf-8"),
        autonomous_manuscript.read_text(encoding="utf-8"),
    )
    output_dir = package_dir / "paper_quality"
    output_dir.mkdir(parents=True, exist_ok=True)

    reviews = []
    for model in args.models:
        result = _call_model(model, prompt, args.max_tokens)
        safe_name = model.replace("/", "_").replace(":", "_")
        raw_content = _content(result)
        parsed = _parse_jsonish(raw_content)
        json_path = output_dir / f"{safe_name}.json"
        md_path = output_dir / f"{safe_name}.md"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md_path.write_text(
            f"# Matched Mini-Manuscript Quality Review: {model}\n\n"
            f"Reviewer route: Monica OpenAI-compatible API\n\n"
            f"```json\n{json.dumps(parsed, indent=2, ensure_ascii=False) if parsed else raw_content}\n```\n",
            encoding="utf-8",
        )
        recommendation = parsed.get("recommendation") if isinstance(parsed, dict) else None
        reviews.append(
            {
                "model": model,
                "status_code": result["status_code"],
                "raw_json": _rel(json_path),
                "markdown": _rel(md_path),
                "parsed": parsed,
                "interpretation": (
                    "co_pilot_preferred"
                    if recommendation == "A"
                    else "autonomous_preferred"
                    if recommendation == "B"
                    else "tie_or_unparsed"
                ),
            }
        )

    successful = [review for review in reviews if review["status_code"] == 200 and review["parsed"]]
    summary = {
        "package_id": manifest["package_id"],
        "status": "mini_manuscript_quality_probe",
        "co_pilot_manuscript": _rel(co_pilot_manuscript),
        "autonomous_manuscript": _rel(autonomous_manuscript),
        "review_count": len(reviews),
        "successful_reviews": len(successful),
        "co_pilot_wins": sum(1 for review in successful if review["parsed"].get("recommendation") == "A"),
        "autonomous_wins": sum(1 for review in successful if review["parsed"].get("recommendation") == "B"),
        "ties": sum(1 for review in successful if review["parsed"].get("recommendation") == "tie"),
        "reviews": reviews,
        "limitations": [
            "Scores mini-manuscripts, not complete generated papers.",
            "Single task and single prospective package.",
            "A is co-pilot and B is autonomous; anonymized to reviewers but not randomized.",
            "Model review is an audit aid, not human expert peer review.",
        ],
    }
    summary_json = output_dir / "summary.json"
    summary_md = output_dir / "summary.md"
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary_md.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary": _rel(summary_json), "markdown": _rel(summary_md)}, indent=2))


if __name__ == "__main__":
    main()
