#!/usr/bin/env python3
"""Audit whether web double-coding reliability is ready for manuscript findings."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


KEY_FIELDS = [
    "dominant_frame",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "embodied_dissolution",
]


@dataclass
class Gate:
    gate: str
    status: str
    evidence: str
    recommendation: str


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def status(ok: bool, warn: bool = False) -> str:
    if ok:
        return "pass"
    return "warn" if warn else "fail"


def clean(value: str | None) -> str:
    return (value or "").strip()


def audit(args: argparse.Namespace) -> list[Gate]:
    main_rows = read_csv(Path(args.main_coding))
    double_rows = read_csv(Path(args.double_coding))
    reliability_rows = read_csv(Path(args.reliability))
    reliability_by_field = {row.get("field", ""): row for row in reliability_rows}
    target_double = max(args.min_double_rows, int(round(len(main_rows) * args.min_double_rate)))

    gates: list[Gate] = []
    gates.append(
        Gate(
            "double_coding_rows",
            status(len(double_rows) >= target_double, warn=len(double_rows) > 0),
            f"double_rows={len(double_rows)}, target={target_double}, main_rows={len(main_rows)}, min_rate={args.min_double_rate}",
            "Double-code at least 20% of the formal sample before reporting content-analysis reliability.",
        )
    )

    covered_ids = {clean(row.get("video_id")) for row in double_rows if clean(row.get("video_id"))}
    gates.append(
        Gate(
            "double_coding_video_ids",
            status(len(covered_ids) >= target_double, warn=bool(covered_ids)),
            f"unique_double_video_ids={len(covered_ids)}, target={target_double}",
            "Double-coding should cover distinct formal sample videos, not repeated rows for the same item.",
        )
    )

    missing_key_fields = [field for field in KEY_FIELDS if field not in reliability_by_field]
    gates.append(
        Gate(
            "key_field_reliability_present",
            "pass" if not missing_key_fields else "fail",
            "missing=" + json.dumps(missing_key_fields, ensure_ascii=False),
            "Reliability report must include dominant frame and core v0.8 body/platform variables.",
        )
    )

    low_key_fields = []
    weak_key_fields = []
    matched_too_low = []
    for field in KEY_FIELDS:
        row = reliability_by_field.get(field, {})
        field_status = clean(row.get("status"))
        matched = int(float(row.get("matched_items") or 0)) if row else 0
        if field_status in {"poor", "insufficient", ""}:
            low_key_fields.append(field)
        elif field_status == "weak":
            weak_key_fields.append(field)
        if matched < args.min_matched_per_field:
            matched_too_low.append(f"{field}:{matched}")

    gates.append(
        Gate(
            "key_field_reliability_quality",
            "pass" if not low_key_fields and not weak_key_fields else "warn" if not low_key_fields else "fail",
            f"low={low_key_fields}, weak={weak_key_fields}",
            "Formal findings should rely on key variables with acceptable or strong reliability; weak variables need reconciliation or cautious qualitative use.",
        )
    )
    gates.append(
        Gate(
            "matched_items_per_key_field",
            status(not matched_too_low),
            "low_matched=" + json.dumps(matched_too_low, ensure_ascii=False),
            "Each key variable should have enough matched double-coded items for reliability statistics.",
        )
    )
    return gates


def write_outputs(gates: list[Gate], output_md: Path, output_json: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    counts = {s: sum(1 for gate in gates if gate.status == s) for s in ["pass", "warn", "fail"]}
    lines = [
        "# 网页人工编码双编码可靠性门槛审计",
        "",
        f"Summary: pass={counts['pass']}, warn={counts['warn']}, fail={counts['fail']}",
        "",
        "| Gate | Status | Evidence | Recommendation |",
        "|---|---|---|---|",
    ]
    for gate in gates:
        evidence = gate.evidence.replace("|", "\\|")
        recommendation = gate.recommendation.replace("|", "\\|")
        lines.append(f"| {gate.gate} | {gate.status} | {evidence} | {recommendation} |")
    lines.extend(["", "## Decision", ""])
    if counts["fail"] == 0 and counts["warn"] == 0:
        lines.append("Double-coding reliability is ready for formal manuscript reporting.")
    else:
        lines.append("Double-coding reliability is not yet ready for formal results. Keep human coding findings out of the manuscript or frame them as pending until this gate passes.")
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output_json.write_text(json.dumps([asdict(gate) for gate in gates], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit web double-coding reliability readiness.")
    parser.add_argument("--main-coding", default="runs/qigong_platform/formal_merge/qigong_human_coding_from_web.csv")
    parser.add_argument("--double-coding", default="runs/qigong_platform/formal_merge/qigong_double_coding_from_web.csv")
    parser.add_argument("--reliability", default="runs/qigong_platform/formal_merge/web_reliability/coding_reliability.csv")
    parser.add_argument("--min-double-rate", type=float, default=0.20)
    parser.add_argument("--min-double-rows", type=int, default=24)
    parser.add_argument("--min-matched-per-field", type=int, default=20)
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/web_reliability_gate.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/web_reliability_gate.json")
    args = parser.parse_args()

    gates = audit(args)
    write_outputs(gates, Path(args.output_md), Path(args.output_json))
    print(args.output_md)


if __name__ == "__main__":
    main()
