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


def _read_excerpt(path: Path, limit: int = 4500) -> str:
    text = _read(path)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n\n[... truncated to {limit} characters for reviewer context ...]"


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
    try:
        payload = response.json()
    except ValueError:
        payload = {
            "error": "non_json_response",
            "text_excerpt": response.text[:2000],
        }
    return {
        "model": model,
        "status_code": response.status_code,
        "response": payload,
    }


def _prompt(paper_path: Path, *, compact: bool = False) -> str:
    default_limit = 700 if compact else 4500
    paper = _read_excerpt(paper_path, 12000) if compact else _read(paper_path)
    audit = _read_excerpt(ROOT / "docs/co_pilot_ai_scientist_v3/audits/claim_evidence_audit.md", default_limit)
    benchmark = _read_excerpt(ROOT / "docs/co_pilot_ai_scientist_v3/benchmark_selection.md", default_limit)
    benchmark_matrix = _read_excerpt(ROOT / "docs/co_pilot_ai_scientist_v3/benchmark_claim_matrix.md", 1600 if compact else 4500)
    prospective_summary = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/audits/prospective_matched_package_summary.md",
        default_limit,
    )
    readiness = _read_excerpt(ROOT / "docs/co_pilot_ai_scientist_v3/audits/top_conference_readiness_audit.md", 2200 if compact else 7000)
    comparison = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_comparison.md",
        default_limit,
    )
    maxcut = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/maxcut_program_search_comparison.md",
        default_limit,
    )
    openreview_regen = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/openreview_guided_regeneration_probe_20260602_073500/README.md",
        default_limit,
    )
    openreview_cross_model = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/openreview_regeneration_cross_model_review_20260602_081500/README.md",
        default_limit,
    )
    review_utility = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/review_utility_map_probe_20260602_071500/README.md",
        default_limit,
    )
    gate_structure = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/gate_structure_ablation_probe_20260602_183000/README.md",
        default_limit,
    )
    gate_outcome = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/gate_outcome_attribution_probe_20260602_191500/README.md",
        default_limit,
    )
    single_gate_artifact = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/single_gate_artifact_ablation_20260602_203000/README.md",
        1200 if compact else 4500,
    )
    metric_gaming_smoke = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/metric_gaming_evaluator_stress_smoke_20260602_171500/README.md",
        default_limit,
    )
    fml_fairness_replay = _read_excerpt(
        ROOT
        / "docs/co_pilot_ai_scientist_v3/experiments/fml_fairness_evaluator_stress_replay_20260602_180000/README.md",
        default_limit,
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

OpenReview-guided regeneration evidence:
```markdown
{openreview_regen}
```

OpenReview cross-model regeneration review:
```markdown
{openreview_cross_model}
```

Review utility map:
```markdown
{review_utility}
```

Gate-structure ablation:
```markdown
{gate_structure}
```

Gate-outcome attribution:
```markdown
{gate_outcome}
```

Single-gate artifact ablation:
```markdown
{single_gate_artifact}
```

Controlled metric-gaming evaluator-stress smoke:
```markdown
{metric_gaming_smoke}
```

FML Fairness evaluator-stress replay:
```markdown
{fml_fairness_replay}
```
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--paper-path",
        default="docs/co_pilot_ai_scientist_v3/paper_en.md",
        help="Markdown manuscript path relative to the repository root.",
    )
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
    parser.add_argument(
        "--compact-context",
        action="store_true",
        help="Use shorter manuscript and artifact excerpts for long-context-sensitive reviewer routes.",
    )
    args = parser.parse_args()

    out_dir = ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    paper_path = ROOT / args.paper_path
    prompt = _prompt(paper_path, compact=args.compact_context)

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
                "paper_path": str(paper_path.relative_to(ROOT)),
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
        json.dumps(
            {
                "paper_path": str(paper_path.relative_to(ROOT)),
                "reviews": list(merged.values()),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"paper_path": str(paper_path.relative_to(ROOT)), "reviews": list(merged.values())}, indent=2))


if __name__ == "__main__":
    main()
