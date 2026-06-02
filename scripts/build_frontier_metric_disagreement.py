#!/usr/bin/env python3
"""Compare short-term review scores with frontier-vector metrics.

This artifact quantifies a key claim of IGRE: human-guided regeneration should
not be judged by one scalar. A regenerated artifact can improve internal review
quality and lexical frontier coverage while moving less directly toward the
frontier centroid in vector space.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
OUT_DIR = DOC_DIR / "experiments" / "frontier_metric_disagreement_20260603_003000"
INTERNAL_DIR = DOC_DIR / "experiments" / "deep_case_internal_review_20260602_224500"
TAXONOMY_SUMMARY = DOC_DIR / "experiments" / "frontier_alignment_taxonomy_20260602_233000" / "summary.json"
VECTOR_SUMMARY = DOC_DIR / "experiments" / "frontier_vector_graph_20260602_234500" / "summary.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _winner_from_delta(delta: float, *, positive: str = "six_gate_hybrid") -> str:
    if delta > 0:
        return positive
    if delta < 0:
        return "raw_review_guided"
    return "tie"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    taxonomy = _load_json(TAXONOMY_SUMMARY)
    vector = _load_json(VECTOR_SUMMARY)

    taxonomy_by_case = {item["case_id"]: item for item in taxonomy["comparisons"]}
    vector_by_case = {item["case_id"]: item for item in vector["per_case"]}
    case_ids = sorted(taxonomy_by_case)

    rows = []
    errors: list[str] = []
    for case_id in case_ids:
        internal_path = INTERNAL_DIR / f"{case_id}.json"
        if not internal_path.exists():
            errors.append(f"missing internal review: {internal_path.relative_to(ROOT)}")
            continue
        internal = _load_json(internal_path)
        tax = taxonomy_by_case[case_id]
        vec = vector_by_case[case_id]

        internal_delta = float(internal["overall_delta_six_gate_minus_raw"])
        lexical_delta = float(tax["delta_six_minus_raw"])
        projection_delta = float(vec["metrics"]["six_minus_raw_projection_gain"])
        cosine_delta = float(vec["metrics"]["six_minus_raw_cosine_gain"])
        winners = {
            "internal_review": _winner_from_delta(internal_delta),
            "lexical_frontier": _winner_from_delta(lexical_delta),
            "vector_projection": _winner_from_delta(projection_delta),
            "frontier_cosine": _winner_from_delta(cosine_delta),
        }
        unique_winners = sorted(set(winners.values()))
        rows.append(
            {
                "case_id": case_id,
                "internal_delta_six_minus_raw": internal_delta,
                "lexical_delta_six_minus_raw": lexical_delta,
                "projection_delta_six_minus_raw": projection_delta,
                "cosine_delta_six_minus_raw": cosine_delta,
                "winners": winners,
                "agreement_all_metrics": len(unique_winners) == 1,
                "has_short_frontier_disagreement": winners["internal_review"] != winners["vector_projection"]
                or winners["internal_review"] != winners["frontier_cosine"],
                "interpretation": (
                    "All short-term and frontier metrics agree."
                    if len(unique_winners) == 1
                    else "Metric disagreement: short-term/internal or lexical gains do not fully determine vector-frontier movement."
                ),
            }
        )

    total = len(rows)
    metric_win_counts = {
        metric: {
            "six_gate_hybrid": sum(1 for row in rows if row["winners"][metric] == "six_gate_hybrid"),
            "raw_review_guided": sum(1 for row in rows if row["winners"][metric] == "raw_review_guided"),
            "tie": sum(1 for row in rows if row["winners"][metric] == "tie"),
        }
        for metric in ["internal_review", "lexical_frontier", "vector_projection", "frontier_cosine"]
    }
    disagreement_count = sum(1 for row in rows if row["has_short_frontier_disagreement"])

    summary = {
        "created_at": _utc_now(),
        "status": "pass" if not errors else "fail",
        "case_count": total,
        "metric_win_counts": metric_win_counts,
        "disagreement_case_count": disagreement_count,
        "disagreement_rate": round(disagreement_count / total, 4) if total else None,
        "rows": rows,
        "errors": errors,
        "claim_boundary": (
            "This is a three-case diagnostic over regenerated mini-artifacts. It supports "
            "the need for multi-metric frontier-aware evaluation, not a general claim that "
            "six-gate regeneration is superior."
        ),
    }

    json_path = OUT_DIR / "summary.json"
    md_path = OUT_DIR / "README.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Frontier Metric Disagreement",
        "",
        "This diagnostic compares short-term/internal review wins with lexical and vector-frontier wins on the three deep regeneration cases.",
        "",
        f"- Case count: `{total}`",
        f"- Disagreement cases: `{disagreement_count}`",
        f"- Disagreement rate: `{summary['disagreement_rate']}`",
        "",
        "## Metric Win Counts",
        "",
        "| Metric | Six-gate wins | Raw wins | Ties |",
        "| --- | ---: | ---: | ---: |",
    ]
    for metric, counts in metric_win_counts.items():
        lines.append(
            f"| `{metric}` | {counts['six_gate_hybrid']} | {counts['raw_review_guided']} | {counts['tie']} |"
        )
    lines.extend(
        [
            "",
            "## Per-Case Matrix",
            "",
            "| Case | Internal delta | Lexical delta | Projection delta | Cosine delta | Disagreement |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['case_id']}` | {row['internal_delta_six_minus_raw']} | "
            f"{row['lexical_delta_six_minus_raw']} | {row['projection_delta_six_minus_raw']} | "
            f"{row['cosine_delta_six_minus_raw']} | `{row['has_short_frontier_disagreement']}` |"
        )
    lines.extend(["", "## Boundary", "", summary["claim_boundary"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"summary": str(json_path.relative_to(ROOT)), "status": summary["status"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
