#!/usr/bin/env python3
"""Mine candidate delayed-value peer-review signals from OpenReview snippets.

This script is a screening stage for Temporal Frontier Replay (TFR). It does
not claim that a review comment is truly delayed-value. Instead, it identifies
comments that are worth expensive replay because they combine:

1. long-horizon directionality, such as frontier, mechanism, theory, scaling,
   generalization, or impact language;
2. short-term friction, such as low scores, rejection, weak evidence, missing
   experiments, unclear claims, or insufficient baselines; and
3. routeability into concrete IGRE gates.

That temporal asymmetry is the user's core hypothesis: a human review can make
the immediate artifact look worse while nudging the research trajectory toward
what later becomes important.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
SOURCE_DIR = DOC_DIR / "experiments" / "review_utility_map_probe_20260602_071500"
OUT_DIR = DOC_DIR / "experiments" / "delayed_value_review_candidate_mining_20260603_001500"


LONG_HORIZON_PATTERNS: dict[str, list[str]] = {
    "frontier_direction": [
        r"\bfuture work\b",
        r"\bextension\b",
        r"\bgo further\b",
        r"\bnext step\b",
        r"\bpromising\b",
        r"\bimportant problem\b",
        r"\bimpact\b",
        r"\bsignificant\b",
    ],
    "mechanism_depth": [
        r"\bmechanism\b",
        r"\bcausal\b",
        r"\bwhy\b",
        r"\bexplain\b",
        r"\bunderstanding\b",
        r"\btheory\b",
        r"\bprinciple\b",
        r"\binsight\b",
    ],
    "generalization_scaling": [
        r"\bgeneraliz",
        r"\bscale\b",
        r"\bscaling\b",
        r"\brobust\b",
        r"\btransfer\b",
        r"\breal[- ]world\b",
        r"\bpractical\b",
        r"\bdeployment\b",
    ],
    "novelty_repositioning": [
        r"\bnovel\b",
        r"\boriginal\b",
        r"\bnew direction\b",
        r"\bprior work\b",
        r"\brelated work\b",
        r"\bstate[- ]of[- ]the[- ]art\b",
        r"\bSOTA\b",
    ],
}

SHORT_TERM_FRICTION_PATTERNS: dict[str, list[str]] = {
    "weak_immediate_evidence": [
        r"\bweak\b",
        r"\binsufficient\b",
        r"\bnot convincing\b",
        r"\bnot convinced\b",
        r"\bunsupported\b",
        r"\blimitation",
        r"\bconcern",
    ],
    "missing_evaluation": [
        r"\bmissing\b",
        r"\bneed(s|ed)?\b",
        r"\bshould\b",
        r"\bbaseline\b",
        r"\bablation\b",
        r"\bbenchmark\b",
        r"\bmetric\b",
        r"\bcomparison\b",
        r"\bevaluation\b",
    ],
    "presentation_or_claim_friction": [
        r"\bunclear\b",
        r"\bclarify\b",
        r"\bconfusing\b",
        r"\boverclaim",
        r"\bclaim\b",
        r"\bconclusion\b",
    ],
}

ROUTEABLE_GATES = {
    "scientific_taste_prior",
    "evaluator_stress_test",
    "frontier_steering",
    "verifiable_micro_evolution",
    "claim_calibration",
    "structured_feedback",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _pattern_hits(text: str, pattern_groups: dict[str, list[str]]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for group, patterns in pattern_groups.items():
        group_hits = [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]
        if group_hits:
            hits[group] = group_hits
    return hits


def _score_hits(hits: dict[str, list[str]]) -> float:
    # Reward breadth first, then repeated evidence within the same group.
    return sum(1.0 + min(2, len(patterns) - 1) * 0.35 for patterns in hits.values())


def _classify(record: dict[str, Any]) -> dict[str, Any]:
    text = str(record.get("text") or "")
    long_hits = _pattern_hits(text, LONG_HORIZON_PATTERNS)
    friction_hits = _pattern_hits(text, SHORT_TERM_FRICTION_PATTERNS)
    long_score = _score_hits(long_hits)
    friction_score = _score_hits(friction_hits)
    gates = set(record.get("primary_gates") or [])
    categories = set(record.get("actionable_categories") or [])
    mean_score = record.get("mean_score")
    low_scored = isinstance(mean_score, (int, float)) and mean_score < 0.6
    rejected = record.get("decision") is False
    routeable = bool(gates & ROUTEABLE_GATES)
    contains_frontier_gate = "frontier_steering" in gates or "frontier_continuation" in categories
    contains_taste_gate = "scientific_taste_prior" in gates or "novelty_positioning" in categories

    temporal_asymmetry = 0.0
    if low_scored:
        temporal_asymmetry += 0.75
    if rejected:
        temporal_asymmetry += 0.75
    if friction_score:
        temporal_asymmetry += min(1.5, friction_score * 0.5)

    delayed_candidate_score = 0.0
    if routeable:
        delayed_candidate_score += 1.0
    if contains_frontier_gate:
        delayed_candidate_score += 1.0
    if contains_taste_gate:
        delayed_candidate_score += 0.75
    delayed_candidate_score += min(3.0, long_score)
    delayed_candidate_score += min(2.0, temporal_asymmetry)
    delayed_candidate_score -= 0.5 * len(record.get("noisy_categories") or [])

    if long_score >= 1.0 and temporal_asymmetry >= 1.0 and routeable:
        label = "delayed_value_replay_candidate"
    elif long_score >= 1.0 and routeable:
        label = "long_horizon_positive_candidate"
    elif friction_score >= 1.0 and routeable:
        label = "short_term_repair_signal"
    elif record.get("noisy_categories") and not record.get("actionable_categories"):
        label = "low_routeability_or_noisy"
    else:
        label = "generic_or_unrouted"

    return {
        **record,
        "long_horizon_hits": long_hits,
        "short_term_friction_hits": friction_hits,
        "long_horizon_score": round(long_score, 4),
        "short_term_friction_score": round(friction_score, 4),
        "temporal_asymmetry_score": round(temporal_asymmetry, 4),
        "delayed_candidate_score": round(max(0.0, delayed_candidate_score), 4),
        "candidate_label": label,
        "routeable": routeable,
        "contains_frontier_gate": contains_frontier_gate,
        "contains_taste_gate": contains_taste_gate,
        "excerpt": re.sub(r"\s+", " ", text).strip()[:700],
    }


def _aggregate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    label_counts = Counter(item["candidate_label"] for item in candidates)
    gate_counts = Counter(gate for item in candidates for gate in item.get("primary_gates") or [])
    delayed = [item for item in candidates if item["candidate_label"] == "delayed_value_replay_candidate"]
    long_positive = [item for item in candidates if item["candidate_label"] == "long_horizon_positive_candidate"]
    short_repair = [item for item in candidates if item["candidate_label"] == "short_term_repair_signal"]
    top_delayed = sorted(delayed, key=lambda item: item["delayed_candidate_score"], reverse=True)[:20]
    top_queue = sorted(
        [item for item in candidates if item["candidate_label"] in {"delayed_value_replay_candidate", "long_horizon_positive_candidate"}],
        key=lambda item: item["delayed_candidate_score"],
        reverse=True,
    )[:30]
    scores = [item["delayed_candidate_score"] for item in candidates]
    return {
        "review_count": len(candidates),
        "paper_count": len({item["paper_index"] for item in candidates}),
        "label_counts": dict(label_counts),
        "gate_counts": dict(gate_counts),
        "delayed_value_replay_candidate_count": len(delayed),
        "long_horizon_positive_candidate_count": len(long_positive),
        "short_term_repair_signal_count": len(short_repair),
        "mean_delayed_candidate_score": round(mean(scores), 4) if scores else 0.0,
        "mean_score_delayed_candidates": round(mean(item["delayed_candidate_score"] for item in delayed), 4) if delayed else 0.0,
        "candidate_rate": round(len(delayed) / len(candidates), 4) if candidates else 0.0,
        "top_delayed_candidates": [_compact(item) for item in top_delayed],
        "tfr_replay_queue": [_compact(item) for item in top_queue],
    }


def _compact(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "review_id": item.get("review_id"),
        "paper_index": item.get("paper_index"),
        "title": item.get("title"),
        "decision": item.get("decision"),
        "mean_score": item.get("mean_score"),
        "candidate_label": item.get("candidate_label"),
        "delayed_candidate_score": item.get("delayed_candidate_score"),
        "long_horizon_score": item.get("long_horizon_score"),
        "temporal_asymmetry_score": item.get("temporal_asymmetry_score"),
        "primary_gates": item.get("primary_gates"),
        "actionable_categories": item.get("actionable_categories"),
        "long_horizon_groups": sorted((item.get("long_horizon_hits") or {}).keys()),
        "friction_groups": sorted((item.get("short_term_friction_hits") or {}).keys()),
        "excerpt": item.get("excerpt"),
    }


def _markdown(summary: dict[str, Any]) -> str:
    aggregate = summary["aggregate"]
    lines = [
        "# Delayed-Value Review Candidate Mining",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Input scored reviews: `{summary['input_scored_reviews']}`",
        f"- Reviews screened: `{aggregate['review_count']}`",
        f"- Papers covered: `{aggregate['paper_count']}`",
        f"- Delayed-value replay candidates: `{aggregate['delayed_value_replay_candidate_count']}`",
        f"- Long-horizon positive candidates: `{aggregate['long_horizon_positive_candidate_count']}`",
        f"- Short-term repair signals: `{aggregate['short_term_repair_signal_count']}`",
        f"- Candidate rate: `{aggregate['candidate_rate']}`",
        "",
        "## Label Counts",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    for label, count in sorted(aggregate["label_counts"].items(), key=lambda item: item[1], reverse=True):
        lines.append(f"| {label} | {count} |")
    lines.extend(["", "## Top Replay Queue", ""])
    for item in aggregate["tfr_replay_queue"][:12]:
        groups = ",".join(item["long_horizon_groups"])
        friction = ",".join(item["friction_groups"])
        gates = ",".join(item.get("primary_gates") or [])
        lines.append(
            f"- `{item['review_id']}` score `{item['delayed_candidate_score']}` "
            f"label `{item['candidate_label']}` gates `{gates}` long `{groups}` "
            f"friction `{friction}`: {item['excerpt']}"
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
            "",
        ]
    )
    return "\n".join(lines)


def _write(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_delayed_value_candidate_mining"
    manifest["delayed_value_review_candidate_mining"] = {
        "run_id": summary["run_id"],
        "summary": summary["summary_path"],
        "candidate_count": summary["aggregate"]["delayed_value_replay_candidate_count"],
        "candidate_rate": summary["aggregate"]["candidate_rate"],
        "claim_boundary": "Candidate screening for TFR replay, not positive delayed-value evidence.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="delayed_value_review_candidate_mining_20260603_001500")
    parser.add_argument("--input-scored-reviews", default=str(SOURCE_DIR / "scored_reviews.json"))
    args = parser.parse_args()

    input_path = Path(args.input_scored_reviews)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    scored_reviews = _load_json(input_path)
    candidates = [_classify(record) for record in scored_reviews]
    aggregate = _aggregate(candidates)
    summary = {
        "run_id": args.run_id,
        "timestamp_utc": _utc_now(),
        "status": "delayed_value_candidate_screening",
        "input_scored_reviews": _rel(input_path),
        "long_horizon_patterns": LONG_HORIZON_PATTERNS,
        "short_term_friction_patterns": SHORT_TERM_FRICTION_PATTERNS,
        "aggregate": aggregate,
        "interpretation": (
            "The screen separates local repair comments from comments that combine "
            "long-horizon directionality with short-term friction. These candidates "
            "are the right inputs for expensive TFR replay: they may not optimize the "
            "next artifact, but they could redirect search toward mechanisms, scaling, "
            "generalization, novelty repositioning, or future impact. The screen also "
            "keeps noisy and generic comments out of the high-cost replay queue."
        ),
        "claim_boundary": (
            "This is candidate mining, not delayed-value evidence. A true delayed-value "
            "case still requires replaying the historical paper under paper-only, "
            "review-guided, and shuffled-review-control conditions and judging the "
            "outputs against later frontier evidence."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [
        _write(OUT_DIR / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2)),
        _write(OUT_DIR / "candidate_reviews.json", json.dumps(candidates, ensure_ascii=False, indent=2)),
        _write(OUT_DIR / "tfr_replay_queue.json", json.dumps(aggregate["tfr_replay_queue"], ensure_ascii=False, indent=2)),
        _write(OUT_DIR / "README.md", _markdown(summary)),
    ]
    summary["summary_path"] = paths[0]
    _write(OUT_DIR / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    _update_manifest(paths + ["scripts/run_delayed_value_review_candidate_mining.py"], summary)
    print(json.dumps({"summary": paths[0], "candidate_count": aggregate["delayed_value_replay_candidate_count"]}, indent=2))


if __name__ == "__main__":
    main()
