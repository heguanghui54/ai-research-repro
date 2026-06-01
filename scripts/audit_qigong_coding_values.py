from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AuditItem:
    gate: str
    status: str
    evidence: str
    recommendation: str


FRAME_VALUES = {
    "instructional_body",
    "therapeutic_body",
    "cultural_body",
    "spectacular_body",
    "social_body",
    "commercial_body",
    "unclear",
}


ALLOWED_VALUES: dict[str, set[str]] = {
    "dominant_frame": FRAME_VALUES,
    "body_visibility": {"full_body", "upper_body", "partial", "close_up", "unclear"},
    "body_count": {"single", "two_three", "group", "unclear"},
    "movement_tempo": {"slow_continuous", "segmented_teaching", "fast_montage", "mixed", "unclear"},
    "camera_relation": {"frontal_teaching", "side_demo", "group_panorama", "cinematic", "talking_head", "mixed", "unclear"},
    "text_occlusion": {"none", "low", "medium", "high", "unclear"},
    "call_to_action": {"none", "follow_along", "check_in", "buy_course", "share_collect", "unclear"},
    "platform_trace": {"none", "hashtag", "hot_music", "bullet_comment", "duet_remix", "live_stream", "unclear"},
    "origin_reference": {
        "none",
        "official_routine",
        "master_teacher",
        "ancient_tradition",
        "medical_health",
        "national_culture",
        "unclear",
    },
    "supplement_mode": {
        "caption",
        "slow_motion",
        "split_screen",
        "comment_checkin",
        "hashtag_topic",
        "commercial_link",
        "ai_filter",
        "music_edit",
        "mixed",
        "none",
        "unclear",
    },
    "binary_reversal": {
        "inner_outer",
        "tradition_modern",
        "teaching_performance",
        "health_traffic",
        "master_influencer",
        "slow_fast",
        "none",
        "unclear",
    },
    "recontextualization_scene": {
        "home_fitness",
        "public_square",
        "scenic_spot",
        "classroom",
        "studio",
        "commerce",
        "challenge",
        "unclear",
    },
    "visibility_centrality": {"low", "medium", "high", "unclear"},
    "tempo_discipline": {"slow_media", "balanced", "accelerated", "montage", "unclear"},
    "efficacy_tagging": {"none", "mild_health", "strong_health", "medicalized", "anxiety_marketing", "unclear"},
    "image_trace_strength": {"none", "weak", "moderate", "strong", "unclear"},
    "media_temporality": {"continuous", "fragmented", "looped", "hot_trend", "live_stream", "mixed", "unclear"},
    "meme_density": {"none", "low", "medium", "high", "unclear"},
    "embodied_dissolution": {"none", "weak", "moderate", "strong", "unclear"},
}


BINARY_FIELDS = {"breath_cue", "mind_cue", "qi_meridian_cue", "risk_cue", "cyber_wellness_symbol"}

REQUIRED_COLUMNS = [
    "video_id",
    "dominant_frame",
    "body_visibility",
    "body_count",
    "movement_tempo",
    "camera_relation",
    "text_occlusion",
    "breath_cue",
    "mind_cue",
    "qi_meridian_cue",
    "risk_cue",
    "call_to_action",
    "platform_trace",
    "origin_reference",
    "supplement_mode",
    "binary_reversal",
    "trace_markers",
    "recontextualization_scene",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "cyber_wellness_symbol",
    "meme_density",
    "embodied_dissolution",
    "coder_id",
]

INTERPRETIVE_FIELDS = [
    "dominant_frame",
    "body_visibility",
    "movement_tempo",
    "origin_reference",
    "supplement_mode",
    "binary_reversal",
    "recontextualization_scene",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "meme_density",
    "embodied_dissolution",
]

V04_FIELDS = [
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "meme_density",
    "embodied_dissolution",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def nonempty(value: str | None) -> bool:
    return bool((value or "").strip())


def completion_rate(rows: list[dict[str, str]], field: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if nonempty(row.get(field))) / len(rows)


def nonhuman_coder_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    flagged = []
    for index, row in enumerate(rows, start=2):
        coder_id = (row.get("coder_id") or "").strip().lower()
        if any(token in coder_id for token in ["llm", "prefill", "model", "ai_"]):
            flagged.append({
                "row": str(index),
                "video_id": row.get("video_id", ""),
                "coder_id": row.get("coder_id", ""),
            })
    return flagged


def split_semicolon(value: str) -> list[str]:
    return [part.strip() for part in value.replace("；", ";").split(";") if part.strip()]


def find_value_errors(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=2):
        video_id = (row.get("video_id") or f"row_{index}").strip()
        for field, allowed in ALLOWED_VALUES.items():
            value = (row.get(field) or "").strip()
            if not value:
                continue
            if value not in allowed:
                errors.append({"row": str(index), "video_id": video_id, "field": field, "value": value})
        for value in split_semicolon(row.get("secondary_frames") or ""):
            if value not in FRAME_VALUES:
                errors.append({"row": str(index), "video_id": video_id, "field": "secondary_frames", "value": value})
        for field in BINARY_FIELDS:
            value = (row.get(field) or "").strip()
            if value and value not in {"0", "1"}:
                errors.append({"row": str(index), "video_id": video_id, "field": field, "value": value})
    return errors


def status_for_completion(rate: float, *, profile: str, threshold: float) -> str:
    if rate >= threshold:
        return "pass"
    if profile == "smoke":
        return "warn"
    return "fail"


def audit(coding: Path, *, profile: str, completion_threshold: float) -> tuple[list[AuditItem], list[dict[str, str]]]:
    fields, rows = read_csv(coding)
    formal = profile == "formal"
    min_rows = 120 if formal else 1
    items: list[AuditItem] = []

    items.append(
        AuditItem(
            "coding_file_exists",
            "pass" if coding.exists() and rows else "fail",
            f"{coding} exists={coding.exists()}, rows={len(rows)}",
            "Complete the platform coding sheet before interpreting content-analysis results.",
        )
    )

    missing_columns = [field for field in REQUIRED_COLUMNS if field not in fields]
    items.append(
        AuditItem(
            "coding_required_columns",
            "pass" if not missing_columns else "fail",
            "missing=" + json.dumps(missing_columns, ensure_ascii=False),
            "Keep the coding sheet aligned with docs/qigong_platform_paper/coding_schema.md.",
        )
    )

    items.append(
        AuditItem(
            "coding_row_count",
            "pass" if len(rows) >= min_rows else "warn" if rows and not formal else "fail",
            f"rows={len(rows)}, target={min_rows}",
            "Formal runs need at least 120 human-coded short-video records; smoke runs only verify mechanics.",
        )
    )

    value_errors = find_value_errors(rows)
    sample_errors = value_errors[:10]
    items.append(
        AuditItem(
            "coding_allowed_values",
            "pass" if not value_errors else "fail",
            f"errors={len(value_errors)}, sample={json.dumps(sample_errors, ensure_ascii=False)}",
            "Fix category spelling before running tables, LLM agreement checks, or manuscript claims.",
        )
    )

    rates = {field: completion_rate(rows, field) for field in INTERPRETIVE_FIELDS if field in fields}
    low_fields = {field: round(rate, 3) for field, rate in rates.items() if rate < completion_threshold}
    average_rate = sum(rates.values()) / len(rates) if rates else 0.0
    items.append(
        AuditItem(
            "coding_interpretive_completion",
            status_for_completion(average_rate, profile=profile, threshold=completion_threshold)
            if not low_fields
            else "warn"
            if profile == "smoke"
            else "fail",
            f"average={average_rate:.3f}, threshold={completion_threshold:.2f}, low_fields={json.dumps(low_fields, ensure_ascii=False)}",
            "Fill the main interpretive variables for nearly all coded rows before treating distributions as findings.",
        )
    )

    v04_rates = {field: completion_rate(rows, field) for field in V04_FIELDS if field in fields}
    v04_low = {field: round(rate, 3) for field, rate in v04_rates.items() if rate < completion_threshold}
    v04_average = sum(v04_rates.values()) / len(v04_rates) if v04_rates else 0.0
    items.append(
        AuditItem(
            "v04_coding_completion",
            status_for_completion(v04_average, profile=profile, threshold=completion_threshold)
            if not v04_low and len(v04_rates) == len(V04_FIELDS)
            else "warn"
            if profile == "smoke"
            else "fail",
            f"average={v04_average:.3f}, threshold={completion_threshold:.2f}, low_fields={json.dumps(v04_low, ensure_ascii=False)}",
            "The v0.4 image-discipline variables are required for the final argument about visibility, tempo, efficacy labels, traces, and embodiment dissolution.",
        )
    )

    coder_rate = completion_rate(rows, "coder_id") if "coder_id" in fields else 0.0
    items.append(
        AuditItem(
            "coder_id_completion",
            status_for_completion(coder_rate, profile=profile, threshold=completion_threshold),
            f"coder_id_completion={coder_rate:.3f}, threshold={completion_threshold:.2f}",
            "Record coder_id so reliability and audit trails remain traceable without exposing personal identities.",
        )
    )

    nonhuman_coders = nonhuman_coder_rows(rows)
    items.append(
        AuditItem(
            "human_coder_id_required",
            "pass" if not nonhuman_coders else "warn" if profile == "smoke" else "fail",
            f"nonhuman_coder_rows={len(nonhuman_coders)}, sample={json.dumps(nonhuman_coders[:10], ensure_ascii=False)}",
            "Formal coding requires human coder IDs. LLM/model/prefill identifiers are allowed only in auxiliary review workbooks.",
        )
    )

    return items, value_errors


def write_outputs(
    items: list[AuditItem],
    errors: list[dict[str, str]],
    output_md: Path,
    output_json: Path,
    output_errors: Path,
) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    counts = {status: sum(1 for item in items if item.status == status) for status in ["pass", "warn", "fail"]}
    lines = [
        "# Health Qigong Coding Values Audit",
        "",
        f"Summary: pass={counts['pass']}, warn={counts['warn']}, fail={counts['fail']}",
        "",
        "| Gate | Status | Evidence | Recommendation |",
        "|---|---|---|---|",
    ]
    for item in items:
        lines.append(f"| {item.gate} | {item.status} | {item.evidence} | {item.recommendation} |")
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output_json.write_text(json.dumps([asdict(item) for item in items], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with output_errors.open("w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["row", "video_id", "field", "value"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(errors)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Health Qigong coding-sheet category values and completion.")
    parser.add_argument("--coding", default="data/qigong_short_video_coding_sheet.csv")
    parser.add_argument("--profile", choices=["formal", "smoke"], default="formal")
    parser.add_argument("--completion-threshold", type=float, default=0.95)
    parser.add_argument("--output-md", default="runs/qigong_platform/audit/coding_values_audit.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/audit/coding_values_audit.json")
    parser.add_argument("--output-errors", default="runs/qigong_platform/audit/coding_value_errors.csv")
    args = parser.parse_args()

    items, errors = audit(Path(args.coding), profile=args.profile, completion_threshold=args.completion_threshold)
    write_outputs(items, errors, Path(args.output_md), Path(args.output_json), Path(args.output_errors))
    print(args.output_md)


if __name__ == "__main__":
    main()
