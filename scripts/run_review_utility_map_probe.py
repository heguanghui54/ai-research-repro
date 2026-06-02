#!/usr/bin/env python3
"""Build a reproducible utility map from OpenReview comments to IGRE gates.

This probe answers a narrower question than the LLM-routed taxonomy probe:
given many real human review snippets, which comment patterns are actually
useful as control signals for an automated research co-pilot?

The script is deliberately deterministic. It uses the cached compact
OpenReview sample produced by `run_expert_review_taste_prior_probe.py`, avoids
per-comment LLM calls, and records both useful and noisy review categories.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
DEFAULT_SAMPLE = (
    DOC_DIR
    / "experiments"
    / "expert_review_taste_prior_probe_20260602_031800"
    / "sample_rows_compact.json"
)


CATEGORIES: dict[str, dict[str, Any]] = {
    "novelty_positioning": {
        "patterns": [
            r"\bnovel\b",
            r"\boriginal\b",
            r"\bincremental\b",
            r"\bnot new\b",
            r"\bsignificant novelty\b",
            r"\bcontribution\b",
            r"\bprior work\b",
            r"\brelated work\b",
            r"\bstate[- ]of[- ]the[- ]art\b",
            r"\bSOTA\b",
        ],
        "gate": "scientific_taste_prior",
        "actionability": 5,
        "useful_signal": "whether the direction is worth pursuing or is too incremental.",
    },
    "evaluation_metric": {
        "patterns": [
            r"\bevaluation\b",
            r"\bexperiment",
            r"\bbenchmark",
            r"\bbaseline",
            r"\bablation",
            r"\bmetric",
            r"\bdataset",
            r"\bcomparison",
            r"\bempirical",
            r"\bresults?",
        ],
        "gate": "evaluator_stress_test",
        "actionability": 5,
        "useful_signal": "which tests, baselines, metrics, or ablations the agent must add.",
    },
    "limitations_claim_boundary": {
        "patterns": [
            r"\blimitation",
            r"\bweakness",
            r"\bclaim",
            r"\boverclaim",
            r"\bconclusion",
            r"\bunsupported",
            r"\binsufficient",
            r"\bthreat",
            r"\bfailure",
            r"\bconcern",
        ],
        "gate": "claim_calibration",
        "actionability": 5,
        "useful_signal": "which claims should be narrowed before paper writing.",
    },
    "clarity_presentation": {
        "patterns": [
            r"\bclarity\b",
            r"\bclear\b",
            r"\bunclear\b",
            r"\bwriting\b",
            r"\bpresentation\b",
            r"\borganization\b",
            r"\bexplain",
            r"\bdefinition",
            r"\bnotation",
        ],
        "gate": "structured_feedback",
        "actionability": 4,
        "useful_signal": "where manuscript structure or explanation blocks progress.",
    },
    "reproducibility_detail": {
        "patterns": [
            r"\breproduc",
            r"\bcode\b",
            r"\bimplementation\b",
            r"\bhyperparameter",
            r"\bsetting",
            r"\bdetails?",
            r"\brelease\b",
            r"\bappendix\b",
        ],
        "gate": "structured_feedback",
        "actionability": 4,
        "useful_signal": "which missing details prevent independent verification.",
    },
    "method_correctness": {
        "patterns": [
            r"\bcorrect",
            r"\bvalid",
            r"\bproof",
            r"\btheorem",
            r"\bassumption",
            r"\bsound",
            r"\bbug",
            r"\berror",
            r"\bflaw",
        ],
        "gate": "evaluator_stress_test",
        "actionability": 5,
        "useful_signal": "which assumptions or implementation details require verification.",
    },
    "frontier_continuation": {
        "patterns": [
            r"\binteresting\b",
            r"\bpromising\b",
            r"\bimportant problem\b",
            r"\bimpact",
            r"\bsignificant\b",
            r"\bfuture work\b",
            r"\bextension",
        ],
        "gate": "frontier_steering",
        "actionability": 3,
        "useful_signal": "which branch has enough upside to continue, if evidence can catch up.",
    },
    "actionable_suggestion": {
        "patterns": [
            r"\bshould\b",
            r"\bneed(s|ed)?\b",
            r"\badd\b",
            r"\binclude\b",
            r"\bcompare\b",
            r"\bclarify\b",
            r"\bprovide\b",
            r"\btry\b",
            r"\bconsider\b",
        ],
        "gate": "structured_feedback",
        "actionability": 4,
        "useful_signal": "direct edit or experiment requests that can become tasks.",
    },
    "generic_praise": {
        "patterns": [
            r"\bgood paper\b",
            r"\bwell written\b",
            r"\bnice\b",
            r"\bstrong\b",
            r"\bsolid\b",
            r"\bexcellent\b",
            r"\bi like\b",
        ],
        "gate": "none",
        "actionability": 1,
        "useful_signal": "usually weak unless paired with a concrete reason.",
    },
    "vague_reaction": {
        "patterns": [
            r"\bnot convinced\b",
            r"\bquestionable\b",
            r"\bconfusing\b",
            r"\bweak\b",
            r"\bminor\b",
            r"\bmajor\b",
            r"\bissue\b",
        ],
        "gate": "triage_before_gate",
        "actionability": 2,
        "useful_signal": "requires decomposition before it can guide an automated step.",
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return float(value)
    return None


def _text_from_snippet(snippet: Any) -> str:
    if not isinstance(snippet, str):
        return ""
    try:
        payload = json.loads(snippet)
    except json.JSONDecodeError:
        payload = None
    if payload is not None and not isinstance(payload, dict):
        return snippet
    review = payload.get("review") if isinstance(payload, dict) else None
    if isinstance(review, dict):
        parts = []
        for key in ["paper_summary", "main_review", "strengths", "weaknesses", "limitations"]:
            value = review.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value)
        if parts:
            return "\n".join(parts)
    # Many cached snippets are intentionally truncated to keep artifacts small,
    # which can make them invalid JSON. Extract the quoted review text fragments
    # directly and ignore numeric metadata fields such as `"clarity": null`,
    # otherwise the classifier would falsely match every review.
    cleaned = snippet.replace("\\n", " ").replace('\\"', '"')
    parts = []
    for label in ["main_review", "paper_summary", "limitations", "strengths", "weaknesses"]:
        pattern = rf'{label}:\s*(.*?)(?:",\s*"|}}\s*$|$)'
        for match in re.finditer(pattern, cleaned, flags=re.I | re.S):
            value = re.sub(r"\s+", " ", match.group(1)).strip()
            if value and value.lower() != "null":
                parts.append(value)
    if parts:
        return "\n".join(parts)
    return re.sub(r'"[a-z_]+":\s*(?:null|[-0-9.]+|true|false),?', " ", cleaned, flags=re.I)


def _review_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for paper_index, row in enumerate(rows):
        score = _numeric(row.get("mean_score"))
        decision = row.get("decision")
        for review_index, snippet in enumerate(row.get("review_snippets") or []):
            text = _text_from_snippet(snippet)
            if len(text.strip()) < 40:
                continue
            records.append(
                {
                    "review_id": f"paper_{paper_index}_review_{review_index}",
                    "paper_index": paper_index,
                    "title": row.get("title"),
                    "decision": decision,
                    "mean_score": score,
                    "text": text[:4000],
                }
            )
    return records


def _matches(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for category, spec in CATEGORIES.items():
        hits = []
        for pattern in spec["patterns"]:
            if re.search(pattern, text, flags=re.I):
                hits.append(pattern)
        if hits:
            found[category] = hits
    return found


def _score_record(record: dict[str, Any]) -> dict[str, Any]:
    matches = _matches(record["text"])
    actionable = [
        category
        for category in matches
        if CATEGORIES[category]["actionability"] >= 4 and CATEGORIES[category]["gate"] != "none"
    ]
    noisy = [
        category
        for category in matches
        if CATEGORIES[category]["actionability"] <= 2 or CATEGORIES[category]["gate"] in {"none", "triage_before_gate"}
    ]
    utility = sum(CATEGORIES[category]["actionability"] for category in actionable)
    utility += 1 if record.get("mean_score") is not None and record["mean_score"] < 0.6 and actionable else 0
    utility -= len(noisy)
    utility = max(0, utility)
    return {
        **record,
        "categories": sorted(matches),
        "actionable_categories": sorted(actionable),
        "noisy_categories": sorted(noisy),
        "utility_score": utility,
        "primary_gates": sorted({CATEGORIES[category]["gate"] for category in actionable}),
    }


def _aggregate(scored: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts: Counter[str] = Counter()
    actionable_counts: Counter[str] = Counter()
    noisy_counts: Counter[str] = Counter()
    gate_counts: Counter[str] = Counter()
    low_score_counts: Counter[str] = Counter()
    accepted_counts: Counter[str] = Counter()
    rejected_counts: Counter[str] = Counter()
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in scored:
        for category in record["categories"]:
            category_counts[category] += 1
            if record.get("mean_score") is not None and record["mean_score"] < 0.6:
                low_score_counts[category] += 1
            if record.get("decision") is True:
                accepted_counts[category] += 1
            elif record.get("decision") is False:
                rejected_counts[category] += 1
            if len(examples[category]) < 3:
                examples[category].append(
                    {
                        "review_id": record["review_id"],
                        "title": record.get("title"),
                        "mean_score": record.get("mean_score"),
                        "decision": record.get("decision"),
                        "excerpt": re.sub(r"\s+", " ", record["text"]).strip()[:360],
                    }
                )
        for category in record["actionable_categories"]:
            actionable_counts[category] += 1
        for category in record["noisy_categories"]:
            noisy_counts[category] += 1
        for gate in record["primary_gates"]:
            gate_counts[gate] += 1

    category_table = []
    total_reviews = max(1, len(scored))
    for category, spec in CATEGORIES.items():
        count = category_counts[category]
        low = low_score_counts[category]
        category_table.append(
            {
                "category": category,
                "count": count,
                "review_share": round(count / total_reviews, 4),
                "actionability": spec["actionability"],
                "gate": spec["gate"],
                "low_score_count": low,
                "low_score_share_within_category": round(low / count, 4) if count else 0.0,
                "accepted_count": accepted_counts[category],
                "rejected_count": rejected_counts[category],
                "useful_signal": spec["useful_signal"],
                "examples": examples.get(category, []),
            }
        )
    category_table.sort(
        key=lambda item: (
            item["actionability"] >= 4,
            item["low_score_count"],
            item["count"],
            item["actionability"],
        ),
        reverse=True,
    )

    utility_scores = [record["utility_score"] for record in scored]
    top_records = sorted(scored, key=lambda record: record["utility_score"], reverse=True)[:12]
    return {
        "category_table": category_table,
        "category_counts": dict(category_counts),
        "actionable_counts": dict(actionable_counts),
        "noisy_counts": dict(noisy_counts),
        "gate_counts": dict(gate_counts),
        "review_count": len(scored),
        "paper_count": len({record["paper_index"] for record in scored}),
        "reviews_with_actionable_signal": sum(1 for record in scored if record["actionable_categories"]),
        "reviews_with_noisy_signal": sum(1 for record in scored if record["noisy_categories"]),
        "mean_utility_score": round(sum(utility_scores) / max(1, len(utility_scores)), 4),
        "top_utility_records": [
            {
                "review_id": record["review_id"],
                "title": record.get("title"),
                "mean_score": record.get("mean_score"),
                "decision": record.get("decision"),
                "utility_score": record["utility_score"],
                "actionable_categories": record["actionable_categories"],
                "primary_gates": record["primary_gates"],
                "excerpt": re.sub(r"\s+", " ", record["text"]).strip()[:480],
            }
            for record in top_records
        ],
    }


def _markdown(summary: dict[str, Any]) -> str:
    aggregate = summary["aggregate"]
    lines = [
        "# OpenReview Review Utility Map Probe",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Input sample: `{summary['input_sample']}`",
        f"- Papers covered: `{aggregate['paper_count']}`",
        f"- Review snippets covered: `{aggregate['review_count']}`",
        f"- Reviews with actionable signal: `{aggregate['reviews_with_actionable_signal']}`",
        f"- Reviews with noisy signal: `{aggregate['reviews_with_noisy_signal']}`",
        f"- Mean utility score: `{aggregate['mean_utility_score']}`",
        "",
        "## Category Utility Ranking",
        "",
        "| Category | Count | Low-score count | Actionability | IGRE gate | Useful signal |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for item in aggregate["category_table"]:
        lines.append(
            f"| {item['category']} | {item['count']} | {item['low_score_count']} | "
            f"{item['actionability']} | {item['gate']} | {item['useful_signal']} |"
        )
    lines.extend(
        [
            "",
            "## Gate Pressure",
            "",
            "| Gate | Actionable review count |",
            "| --- | ---: |",
        ]
    )
    for gate, count in sorted(aggregate["gate_counts"].items(), key=lambda item: item[1], reverse=True):
        lines.append(f"| {gate} | {count} |")
    lines.extend(["", "## Top Utility Review Examples", ""])
    for record in aggregate["top_utility_records"][:8]:
        cats = ", ".join(record["actionable_categories"])
        gates = ", ".join(record["primary_gates"])
        lines.append(
            f"- `{record['review_id']}` score={record.get('mean_score')} gates={gates} "
            f"categories={cats}: {record['excerpt']}"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            summary["interpretation"],
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
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
    manifest["status"] = "pilot_package_with_review_utility_map_probe"
    manifest["review_utility_map_probe"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "review_count": summary["aggregate"]["review_count"],
        "paper_count": summary["aggregate"]["paper_count"],
        "reviews_with_actionable_signal": summary["aggregate"]["reviews_with_actionable_signal"],
        "gate_counts": summary["aggregate"]["gate_counts"],
        "claim_boundary": "Deterministic OpenReview utility map; not causal proof of final paper improvement.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"review_utility_map_probe_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--input-sample", default=str(DEFAULT_SAMPLE))
    args = parser.parse_args()

    input_sample = Path(args.input_sample)
    if not input_sample.is_absolute():
        input_sample = ROOT / input_sample
    rows = _load_json(input_sample)
    records = _review_records(rows)
    scored = [_score_record(record) for record in records]
    aggregate = _aggregate(scored)

    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "review_utility_map_probe",
        "input_sample": _rel(input_sample),
        "category_definitions": CATEGORIES,
        "aggregate": aggregate,
        "interpretation": (
            "Across the sampled OpenReview snippets, the strongest useful signals "
            "are not generic approval. They are review patterns that can be routed "
            "to concrete IGRE gates: novelty/positioning to scientific taste priors, "
            "evaluation and correctness concerns to evaluator stress tests, "
            "limitations to claim calibration, and clarity/reproducibility requests "
            "to structured feedback. Generic praise and vague reactions are recorded "
            "as low-utility unless they co-occur with actionable details."
        ),
        "claim_boundary": (
            "This deterministic map shows how real human reviews can be converted "
            "into workflow control signals and which categories are more actionable. "
            "It does not prove causal improvement in final papers; that requires "
            "matched regeneration or prospective co-pilot experiments."
        ),
    }

    out_dir = DOC_DIR / "experiments" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        _write(out_dir / "scored_reviews.json", json.dumps(scored, ensure_ascii=False, indent=2)),
        _write(out_dir / "category_utility_table.json", json.dumps(aggregate["category_table"], ensure_ascii=False, indent=2)),
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
    _update_manifest(paths + ["scripts/run_review_utility_map_probe.py"], summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
