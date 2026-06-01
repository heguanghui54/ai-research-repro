#!/usr/bin/env python3
"""Run a Monica-routed paper-quality review for Co-Pilot AI Scientist v3."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _call_model(model: str, prompt: str, max_tokens: int) -> dict:
    base_url = os.environ.get("MONICA_BASE_URL", "https://openapi.monica.im/v1").rstrip("/")
    api_key = os.environ["MONICA_API_KEY"]
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a strict but constructive ML/NLP systems paper reviewer. "
                        "Score only what is supported by the provided manuscript and artifacts. "
                        "Do not invent missing experiments."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
        },
        timeout=180,
    )
    payload = response.json()
    return {
        "model": model,
        "status_code": response.status_code,
        "response": payload,
    }


def _prompt() -> str:
    paper = _read(ROOT / "docs/co_pilot_ai_scientist_v3/paper_en.md")
    audit = _read(ROOT / "docs/co_pilot_ai_scientist_v3/audits/claim_evidence_audit.md")
    benchmark = _read(ROOT / "docs/co_pilot_ai_scientist_v3/benchmark_selection.md")
    benchmark_matrix = _read(ROOT / "docs/co_pilot_ai_scientist_v3/benchmark_claim_matrix.md")
    prospective_summary = _read(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/audits/prospective_matched_package_summary.md"
    )
    readiness = _read(ROOT / "docs/co_pilot_ai_scientist_v3/audits/top_conference_readiness_audit.md")
    comparison = _read(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_comparison.md"
    )
    maxcut = _read(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/maxcut_program_search_comparison.md"
    )
    return f"""Review the following draft as if it were a submission targetting a strong ML/NLP systems venue.

Return Markdown with these sections:
1. Executive recommendation: Accept / Weak accept / Borderline / Weak reject / Reject.
2. Rubric table with integer scores from 1 to 5 for novelty, rigor, clarity, evidence, reproducibility, and significance.
3. Top three strengths.
4. Top five blocking weaknesses for top-conference readiness.
5. Concrete required revisions for the next draft.
6. One paragraph of safer contribution wording.

Manuscript:
```markdown
{paper}
```

Claim-evidence audit:
```markdown
{audit}
```

Benchmark selection:
```markdown
{benchmark}
```

Benchmark-to-claim matrix:
```markdown
{benchmark_matrix}
```

Prospective matched-budget package summary:
```markdown
{prospective_summary}
```

Top-conference readiness audit:
```markdown
{readiness}
```

MLAgentBench comparison:
```markdown
{comparison}
```

Max-Cut program-search comparison:
```markdown
{maxcut}
```
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gpt-4o-mini", "claude-3-7-sonnet-latest"],
    )
    parser.add_argument(
        "--output-dir",
        default="docs/co_pilot_ai_scientist_v3/audits/paper_quality_reviews",
    )
    parser.add_argument("--max-tokens", type=int, default=1800)
    args = parser.parse_args()

    out_dir = ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt = _prompt()

    summaries = []
    for model in args.models:
        result = _call_model(model, prompt, args.max_tokens)
        safe_name = model.replace("/", "_").replace(":", "_")
        json_path = out_dir / f"{safe_name}.json"
        md_path = out_dir / f"{safe_name}.md"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        content = ""
        try:
            content = result["response"]["choices"][0]["message"].get("content", "")
        except (KeyError, IndexError, TypeError):
            content = json.dumps(result["response"], ensure_ascii=False, indent=2)
        md_path.write_text(
            f"# Paper Quality Review: {model}\n\n"
            f"Reviewer route: Monica OpenAI-compatible API\n\n"
            f"{content.strip()}\n",
            encoding="utf-8",
        )
        summaries.append(
            {
                "model": model,
                "status_code": result["status_code"],
                "markdown": str(md_path.relative_to(ROOT)),
            }
        )

    summary_path = out_dir / "summary.json"
    existing: dict[str, object] = {"reviews": []}
    if summary_path.exists():
        try:
            existing = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {"reviews": []}
    merged = {item["model"]: item for item in existing.get("reviews", [])}
    for item in summaries:
        merged[item["model"]] = item
    summary_path.write_text(
        json.dumps({"reviews": list(merged.values())}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"reviews": list(merged.values())}, indent=2))


if __name__ == "__main__":
    main()
