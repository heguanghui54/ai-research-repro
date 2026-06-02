#!/usr/bin/env python3
"""Create a blind human-expert review packet for OpenReview regeneration pairs."""

from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
DEFAULT_REGEN = (
    DOC_DIR
    / "experiments"
    / "openreview_guided_regeneration_probe_20260602_073500"
    / "summary.json"
)
DEFAULT_EQUAL_CONTEXT = (
    DOC_DIR
    / "experiments"
    / "openreview_equal_context_ablation_20260602_142000"
    / "summary.json"
)


RUBRIC_FIELDS = [
    "problem_framing",
    "method_specificity",
    "experiment_design",
    "limitation_honesty",
    "claim_calibration",
    "overall_quality",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> str:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return _rel(path)


def _artifact_text(artifact: dict[str, Any]) -> str:
    lines = [
        f"Core contribution: {artifact.get('core_contribution', '')}",
        "",
        f"Method sketch: {artifact.get('method_sketch', '')}",
        "",
        f"Experiment plan: {artifact.get('experiment_plan', '')}",
        "",
        f"Limitations: {artifact.get('limitations', '')}",
        "",
        f"Claim boundary: {artifact.get('claim_boundary', '')}",
        "",
        "Mini-paper artifact:",
        str(artifact.get("mini_paper_artifact", "")),
    ]
    if artifact.get("review_insights_used"):
        # Do not include the label in the blind-facing text. The insights are
        # intentionally omitted so reviewers judge only the resulting artifact.
        pass
    if artifact.get("generic_review_pressures_used"):
        pass
    return "\n".join(lines).strip()


def _control_by_id(equal_context_summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    path = ROOT / Path(equal_context_summary["summary_path"]).parent / "context_control_artifacts.json"
    control = _load_json(path)
    return {
        item["paper_id"]: item["context_control_regeneration"]
        for item in control.get("papers", [])
    }


def _make_pairs(
    *,
    regeneration_summary: dict[str, Any],
    equal_context_summary: dict[str, Any],
    seed: int,
    condition: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    papers_by_id = {paper["paper_id"]: paper for paper in regeneration_summary["selected_papers"]}
    regen_by_id = {
        paper["paper_id"]: paper
        for paper in regeneration_summary["regenerations"]["papers"]
    }
    control_by_id = _control_by_id(equal_context_summary)
    rng = random.Random(seed)
    pairs = []
    key: dict[str, Any] = {
        "seed": seed,
        "condition": condition,
        "mapping": {},
    }
    for i, paper_id in enumerate(sorted(regen_by_id), start=1):
        paper = papers_by_id[paper_id]
        source_a = regen_by_id[paper_id]["review_guided_regeneration"]
        if condition == "baseline":
            source_b = regen_by_id[paper_id]["baseline_regeneration"]
            source_b_label = "baseline_title_abstract_only"
        elif condition == "equal_context":
            source_b = control_by_id[paper_id]
            source_b_label = "context_control_unrelated_reviews"
        else:
            raise ValueError(f"unsupported condition: {condition}")

        variants = [
            ("review_guided", source_a),
            (source_b_label, source_b),
        ]
        rng.shuffle(variants)
        pair_id = f"pair_{i:02d}"
        label_map = {
            "A": variants[0][0],
            "B": variants[1][0],
        }
        key["mapping"][pair_id] = {
            "paper_id": paper_id,
            "title": paper.get("title"),
            "A": label_map["A"],
            "B": label_map["B"],
        }
        pairs.append(
            {
                "pair_id": pair_id,
                "paper_id": paper_id,
                "title": paper.get("title"),
                "abstract_excerpt": paper.get("abstract_excerpt"),
                "variant_A": _artifact_text(variants[0][1]),
                "variant_B": _artifact_text(variants[1][1]),
            }
        )
    return pairs, key


def _instructions(condition: str) -> str:
    comparator = (
        "title/abstract-only baseline"
        if condition == "baseline"
        else "matched-length unrelated-review context control"
    )
    fields = "\n".join(f"- `{field}`: 1-5" for field in RUBRIC_FIELDS)
    return f"""# Human Expert Blind Review Instructions

You are evaluating anonymized mini-paper artifacts generated from real
OpenReview ML/AI papers. Each pair contains two artifacts for the same source
paper. One artifact was generated with paper-specific OpenReview feedback. The
other was generated with the {comparator}. The order is randomized.

Please do not try to identify which condition is which. Judge only the artifact
quality.

For each pair, score Variant A and Variant B on:

{fields}

Use integers from 1 to 5:

- 1 = poor or unsupported
- 2 = weak
- 3 = acceptable
- 4 = strong
- 5 = excellent

Then choose `A`, `B`, or `tie` as the pair winner and add a short rationale.

Primary question:

Does one artifact better reflect expert scientific taste and insight through
clearer problem framing, more specific method design, stronger experiments,
more honest limitations, and better claim calibration?

Important boundaries:

- These are short regenerated artifacts, not complete papers.
- Do not judge whether the original paper should be accepted.
- Do not reward verbosity.
- Prefer concrete experimental and claim-calibration improvements over generic
  polish.
"""


def _pair_markdown(pair: dict[str, Any]) -> str:
    return f"""# {pair['pair_id']}: Blind Pair

## Source Paper Context

Title: {pair['title']}

Abstract excerpt:

{pair['abstract_excerpt']}

## Variant A

{pair['variant_A']}

## Variant B

{pair['variant_B']}
"""


def _score_sheet_csv(path: Path, pairs: list[dict[str, Any]]) -> str:
    rows = []
    for pair in pairs:
        row = {
            "reviewer_id": "",
            "pair_id": pair["pair_id"],
            "winner": "",
            "rationale": "",
        }
        for side in ["A", "B"]:
            for field in RUBRIC_FIELDS:
                row[f"{side}_{field}"] = ""
        rows.append(row)
    fieldnames = ["reviewer_id", "pair_id", "winner"]
    for side in ["A", "B"]:
        for field in RUBRIC_FIELDS:
            fieldnames.append(f"{side}_{field}")
    fieldnames.append("rationale")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return _rel(path)


def _summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# Human Expert Blind Review Packet",
        "",
        f"- Packet ID: `{summary['packet_id']}`",
        f"- Timestamp UTC: `{summary['timestamp_utc']}`",
        f"- Condition: `{summary['condition']}`",
        f"- Pair count: `{summary['pair_count']}`",
        f"- Source regeneration run: `{summary['source_regeneration_run']}`",
        f"- Equal-context source run: `{summary['equal_context_run']}`",
        "",
        "## Files",
        "",
    ]
    for path in summary["reviewer_visible_files"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Status",
            "",
            "This packet prepares blind human expert evaluation. It does not contain",
            "completed human ratings yet. The condition key is stored separately in",
            "`condition_key.json` and should not be shown to reviewers.",
        ]
    )
    return "\n".join(lines)


def _update_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_human_expert_blind_review_packet"
    manifest["human_expert_blind_review_packet"] = {
        "packet_id": summary["packet_id"],
        "summary": summary["summary_path"],
        "condition": summary["condition"],
        "pair_count": summary["pair_count"],
        "status": "packet_prepared_no_human_ratings_yet",
        "claim_boundary": "Prepared blind review materials only; no independent human expert results are claimed.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-id", default=f"human_expert_blind_review_packet_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--condition", choices=["baseline", "equal_context"], default="equal_context")
    parser.add_argument("--seed", type=int, default=20260602)
    parser.add_argument("--regeneration-summary", default=str(DEFAULT_REGEN.relative_to(ROOT)))
    parser.add_argument("--equal-context-summary", default=str(DEFAULT_EQUAL_CONTEXT.relative_to(ROOT)))
    args = parser.parse_args()

    regeneration = _load_json(ROOT / args.regeneration_summary)
    equal_context = _load_json(ROOT / args.equal_context_summary)
    pairs, key = _make_pairs(
        regeneration_summary=regeneration,
        equal_context_summary=equal_context,
        seed=args.seed,
        condition=args.condition,
    )

    out_dir = DOC_DIR / "experiments" / args.packet_id
    pair_dir = out_dir / "pairs"
    pair_dir.mkdir(parents=True, exist_ok=True)

    paths = [
        _write(out_dir / "instructions.md", _instructions(args.condition)),
        _write(out_dir / "pairs.json", json.dumps(pairs, ensure_ascii=False, indent=2)),
        _write(out_dir / "condition_key.json", json.dumps(key, ensure_ascii=False, indent=2)),
        _score_sheet_csv(out_dir / "score_sheet_template.csv", pairs),
    ]
    for pair in pairs:
        paths.append(_write(pair_dir / f"{pair['pair_id']}.md", _pair_markdown(pair)))

    summary: dict[str, Any] = {
        "packet_id": args.packet_id,
        "timestamp_utc": _utc_now(),
        "status": "blind_review_packet_prepared_no_human_ratings_yet",
        "condition": args.condition,
        "seed": args.seed,
        "pair_count": len(pairs),
        "source_regeneration_run": regeneration["run_id"],
        "source_regeneration_summary": args.regeneration_summary,
        "equal_context_run": equal_context["run_id"],
        "equal_context_summary": args.equal_context_summary,
        "reviewer_visible_files": [
            _rel(out_dir / "instructions.md"),
            _rel(out_dir / "score_sheet_template.csv"),
            *[_rel(pair_dir / f"{pair['pair_id']}.md") for pair in pairs],
        ],
        "hidden_files": [_rel(out_dir / "condition_key.json")],
        "claim_boundary": "Packet preparation only; no human expert ratings have been collected.",
    }
    summary_path = out_dir / "README.md"
    summary["summary_path"] = _rel(summary_path)
    paths.append(_write(summary_path, _summary_md(summary)))
    summary_json = out_dir / "summary.json"
    paths.append(_write(summary_json, json.dumps(summary, ensure_ascii=False, indent=2)))
    summary["artifacts_written"] = paths
    _write(summary_json, json.dumps(summary, ensure_ascii=False, indent=2))
    _update_manifest(paths + ["scripts/create_human_expert_blind_review_packet.py"], summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
