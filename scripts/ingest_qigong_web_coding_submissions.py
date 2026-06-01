from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


OUTPUT_FIELDS = [
    "video_id",
    "platform",
    "url_hash",
    "collection_date",
    "keyword",
    "duration_sec",
    "title",
    "hashtags",
    "author_type",
    "like_count",
    "comment_count",
    "share_count",
    "dominant_frame",
    "secondary_frames",
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
    "notes",
]

WEB_FIELDS = [
    "dominant_frame",
    "secondary_frames",
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
    "notes",
]

CORE_FIELDS = [
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
    "recontextualization_scene",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "cyber_wellness_symbol",
    "meme_density",
    "embodied_dissolution",
]

VALUE_MAPS = {
    "supplement_mode": {
        "caption_explanation": "caption",
        "music_reframing": "music_edit",
        "comment_interaction": "comment_checkin",
        "hashtag_recontextualization": "hashtag_topic",
        "commercial_linkage": "commercial_link",
    },
}


def clean(value: object) -> str:
    return str(value or "").strip()


def normalize_task_role(value: object) -> str:
    role = clean(value).lower()
    if role in {"double", "double_check", "double-check", "secondary", "review"}:
        return "double_check"
    return role or "missing"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def video_id(row: dict[str, str]) -> str:
    return clean(row.get("video_id") or row.get("\ufeffvideo_id"))


def normalize_field(field: str, value: str) -> str:
    value = clean(value)
    return VALUE_MAPS.get(field, {}).get(value, value)


def watched(row: dict[str, str]) -> bool:
    return clean(row.get("watched")).lower() in {"true", "1", "yes", "y"}


def submission_is_complete(row: dict[str, str]) -> bool:
    return watched(row) and all(clean(row.get(field)) for field in CORE_FIELDS)


def coder_id_from_submission(row: dict[str, str]) -> str:
    code = clean(row.get("student_code")).lower()
    return f"web_{code}" if code else "web_unknown"


def apply_submission(target: dict[str, str], submission: dict[str, str], *, overwrite: bool) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for field in WEB_FIELDS:
        value = normalize_field(field, submission.get(field, ""))
        if not value:
            continue
        old = clean(target.get(field))
        if old and old != value and not overwrite:
            continue
        if old != value:
            target[field] = value
            changes.append({"video_id": video_id(target), "field": field, "old_value": old, "new_value": value})
    coder_id = coder_id_from_submission(submission)
    if clean(target.get("coder_id")) != coder_id and (overwrite or not clean(target.get("coder_id"))):
        changes.append({"video_id": video_id(target), "field": "coder_id", "old_value": clean(target.get("coder_id")), "new_value": coder_id})
        target["coder_id"] = coder_id
    return changes


def row_for_double_check(base_by_id: dict[str, dict[str, str]], submission: dict[str, str]) -> dict[str, str]:
    base = dict(base_by_id.get(video_id(submission), {"video_id": video_id(submission)}))
    for field in WEB_FIELDS:
        base[field] = normalize_field(field, submission.get(field, ""))
    base["coder_id"] = coder_id_from_submission(submission)
    return {field: clean(base.get(field)) for field in OUTPUT_FIELDS}


def write_report(path: Path, audit: dict[str, object]) -> None:
    lines = [
        "# Web Coding Submission Ingest Audit",
        "",
        f"- Web export: `{audit['web_export']}`",
        f"- Base coding sheet: `{audit['base_coding']}`",
        f"- Output main coding: `{audit['output_main']}`",
        f"- Output double-check coding: `{audit['output_double']}`",
        f"- Submission rows: {audit['submission_rows']}",
        f"- Complete submission rows: {audit['complete_submission_rows']}",
        f"- Primary complete rows: {audit['primary_complete_rows']}",
        f"- Double-check complete rows: {audit['double_check_complete_rows']}",
        f"- Changed values: {audit['changed_values']}",
        f"- Complete main coding rows after merge: {audit['complete_main_rows_after_merge']}",
        f"- Missing export columns: {audit['missing_export_columns']}",
        f"- Unknown video IDs: {audit['unknown_video_ids'][:30]}",
        f"- Incomplete submission IDs: {audit['incomplete_submission_ids'][:30]}",
        f"- Ready for formal audit: {audit['ready_for_formal_audit']}",
        "",
        "Run the formal value audit on the output main coding sheet only after all primary tasks are complete.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Supabase web coding submissions into the formal Health Qigong coding sheet.")
    parser.add_argument("--web-export", default="runs/qigong_platform/formal_merge/web_coding_submissions_export.csv")
    parser.add_argument("--base-coding", default="data/qigong_short_video_coding_sheet_formal.csv")
    parser.add_argument("--output-main", default="runs/qigong_platform/formal_merge/qigong_human_coding_from_web.csv")
    parser.add_argument("--output-double", default="runs/qigong_platform/formal_merge/qigong_double_coding_from_web.csv")
    parser.add_argument("--change-log", default="runs/qigong_platform/formal_merge/web_coding_ingest_changes.csv")
    parser.add_argument("--audit-json", default="runs/qigong_platform/formal_merge/web_coding_ingest_audit.json")
    parser.add_argument("--audit-md", default="runs/qigong_platform/formal_merge/web_coding_ingest_audit.md")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    base_fields, base_rows = read_csv(Path(args.base_coding))
    export_fields, submissions = read_csv(Path(args.web_export))
    if not base_rows:
        raise SystemExit(f"base coding sheet missing or empty: {args.base_coding}")
    if not base_fields:
        base_fields = OUTPUT_FIELDS
    missing_export_columns = [field for field in ["video_id", "student_code", "task_role", "watched", *CORE_FIELDS] if field not in export_fields]
    base_by_id = {video_id(row): row for row in base_rows}

    unknown_video_ids = [video_id(row) for row in submissions if video_id(row) not in base_by_id]
    incomplete = [video_id(row) for row in submissions if not submission_is_complete(row)]
    changes: list[dict[str, str]] = []
    complete_primary = []
    double_rows = []
    for submission in submissions:
        if not submission_is_complete(submission) or video_id(submission) not in base_by_id:
            continue
        if normalize_task_role(submission.get("task_role")) == "double_check":
            double_rows.append(row_for_double_check(base_by_id, submission))
            continue
        complete_primary.append(submission)
        changes.extend(apply_submission(base_by_id[video_id(submission)], submission, overwrite=args.overwrite))

    output_fields = [field for field in OUTPUT_FIELDS if field in base_fields] + [field for field in OUTPUT_FIELDS if field not in base_fields]
    main_rows = [{field: clean(row.get(field)) for field in output_fields} for row in base_rows]
    write_csv(Path(args.output_main), output_fields, main_rows)
    write_csv(Path(args.output_double), OUTPUT_FIELDS, double_rows)
    write_csv(Path(args.change_log), ["video_id", "field", "old_value", "new_value"], changes)

    complete_main = sum(1 for row in main_rows if all(clean(row.get(field)) for field in CORE_FIELDS) and clean(row.get("coder_id")))
    by_student = Counter(clean(row.get("student_code")) for row in submissions if clean(row.get("student_code")))
    audit = {
        "web_export": args.web_export,
        "base_coding": args.base_coding,
        "output_main": args.output_main,
        "output_double": args.output_double,
        "submission_rows": len(submissions),
        "complete_submission_rows": sum(1 for row in submissions if submission_is_complete(row)),
        "primary_complete_rows": len(complete_primary),
        "double_check_complete_rows": len(double_rows),
        "changed_values": len(changes),
        "complete_main_rows_after_merge": complete_main,
        "missing_export_columns": missing_export_columns,
        "unknown_video_ids": unknown_video_ids,
        "incomplete_submission_ids": incomplete,
        "students": dict(sorted(by_student.items())),
        "ready_for_formal_audit": not missing_export_columns and not unknown_video_ids and len(complete_primary) >= 120 and complete_main >= 120,
    }
    Path(args.audit_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_json).write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(Path(args.audit_md), audit)
    print(args.output_main)
    print(args.output_double)
    print(args.audit_md)
    print(args.audit_json)


if __name__ == "__main__":
    main()
