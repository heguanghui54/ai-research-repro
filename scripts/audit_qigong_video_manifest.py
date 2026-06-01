from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


RIGHTS_STATUSES = {"rights_confirmed", "manual_view_only", "metadata_only", "no"}
CASE_ROLES = {"standard_reference", "platform_variant", "hf_baseline", "pilot"}


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def included_metadata_hashes(metadata_path: Path) -> set[str]:
    rows = read_rows(metadata_path)
    return {
        (row.get("url_hash") or "").strip()
        for row in rows
        if (row.get("include_status") or "").strip() == "included" and (row.get("url_hash") or "").strip()
    }


def add_gate(rows: list[dict[str, str]], gate: str, status: str, evidence: str, recommendation: str) -> None:
    rows.append({
        "gate": gate,
        "status": status,
        "evidence": evidence,
        "recommendation": recommendation,
    })


def status_from(ok: bool, *, formal: bool) -> str:
    if ok:
        return "pass"
    return "fail" if formal else "warn"


def audit(
    *,
    manifest_rows: list[dict[str, str]],
    metadata_hashes: set[str],
    formal: bool,
    min_cases: int,
    min_existing_local: int,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    nonempty = [row for row in manifest_rows if (row.get("video_id") or "").strip()]
    local_rows = [row for row in nonempty if (row.get("local_video_path") or "").strip()]
    existing_local = [
        row
        for row in local_rows
        if Path(row.get("local_video_path", "").strip()).expanduser().exists()
    ]
    role_counts = Counter((row.get("case_role") or "").strip() for row in nonempty if (row.get("case_role") or "").strip())
    group_counts = Counter((row.get("comparison_group") or "").strip() for row in nonempty if (row.get("comparison_group") or "").strip())
    routine_counts = Counter((row.get("routine") or "").strip() for row in nonempty if (row.get("routine") or "").strip())
    invalid_rights = [
        row.get("video_id", "")
        for row in nonempty
        if (row.get("rights_status") or "").strip() not in RIGHTS_STATUSES
    ]
    invalid_roles = [
        row.get("video_id", "")
        for row in nonempty
        if (row.get("case_role") or "").strip() and (row.get("case_role") or "").strip() not in CASE_ROLES
    ]
    local_without_rights = [
        row.get("video_id", "")
        for row in local_rows
        if (row.get("rights_status") or "").strip() != "rights_confirmed"
    ]
    platform_hashes = [
        (row.get("url_hash") or "").strip()
        for row in nonempty
        if (row.get("case_role") or "").strip() == "platform_variant"
    ]
    platform_hash_missing = sum(1 for value in platform_hashes if not value)
    platform_hash_unmatched = sum(1 for value in platform_hashes if value and metadata_hashes and value not in metadata_hashes)
    expected_use_missing = [row.get("video_id", "") for row in nonempty if not (row.get("expected_use") or "").strip()]

    add_gate(
        rows,
        "typical_case_count",
        status_from(len(nonempty) >= min_cases, formal=formal),
        f"manifest_rows={len(nonempty)}, target>={min_cases}",
        "Prepare 3-5 typical cases before claiming embodied video evidence.",
    )
    add_gate(
        rows,
        "local_video_files",
        status_from(len(existing_local) >= min_existing_local, formal=formal),
        f"listed_local={len(local_rows)}, existing_local={len(existing_local)}, target>={min_existing_local}",
        "Pose/video feature extraction requires legally stored local files.",
    )
    add_gate(
        rows,
        "standard_reference_present",
        status_from(role_counts.get("standard_reference", 0) >= 1, formal=formal),
        f"case_roles={dict(role_counts)}",
        "Include at least one official or standard reference video.",
    )
    add_gate(
        rows,
        "platform_variant_present",
        status_from(role_counts.get("platform_variant", 0) >= 2, formal=formal),
        f"case_roles={dict(role_counts)}",
        "Include at least two platform-variant videos for comparison.",
    )
    add_gate(
        rows,
        "comparison_groups_present",
        status_from("official" in group_counts and "platform" in group_counts, formal=formal),
        f"comparison_groups={dict(group_counts)}",
        "Comparison groups should distinguish official/standard and platform-variant cases.",
    )
    add_gate(
        rows,
        "routine_or_segment_recorded",
        status_from(len(routine_counts) >= 1 and not expected_use_missing, formal=formal),
        f"routines={dict(routine_counts)}, expected_use_missing={expected_use_missing}",
        "Record routine/action segment and expected analytic use for every typical case.",
    )
    add_gate(
        rows,
        "rights_status_valid",
        status_from(not invalid_rights, formal=formal),
        f"invalid_rights_video_ids={invalid_rights}",
        "Use rights_confirmed, manual_view_only, metadata_only, or no.",
    )
    add_gate(
        rows,
        "case_role_valid",
        status_from(not invalid_roles, formal=formal),
        f"invalid_role_video_ids={invalid_roles}",
        "Use standard_reference, platform_variant, hf_baseline, or pilot.",
    )
    add_gate(
        rows,
        "local_files_rights_confirmed",
        status_from(not local_without_rights, formal=formal),
        f"local_without_rights_confirmed={local_without_rights}",
        "Any local file used for feature extraction should be rights_confirmed.",
    )
    add_gate(
        rows,
        "platform_variant_traceability",
        status_from(platform_hash_missing == 0 and platform_hash_unmatched == 0, formal=formal),
        f"platform_hash_missing={platform_hash_missing}, platform_hash_unmatched={platform_hash_unmatched}, metadata_hashes_available={len(metadata_hashes)}",
        "Platform variants should trace back to included metadata via url_hash when possible.",
    )
    return rows


def write_outputs(rows: list[dict[str, str]], output_md: Path, output_json: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Typical-Case Video Manifest Audit", ""]
    lines.append("| Gate | Status | Evidence | Recommendation |")
    lines.append("|---|---|---|---|")
    for row in rows:
        lines.append(f"| {row['gate']} | {row['status']} | {row['evidence']} | {row['recommendation']} |")
    non_pass = [row for row in rows if row["status"] != "pass"]
    lines.extend(["", "## Decision", ""])
    if not non_pass:
        lines.append("Typical-case video manifest is ready for formal embodied video analysis.")
    else:
        lines.append("Typical-case video manifest is not yet sufficient for submission-level embodied video claims. Address non-pass gates or keep video evidence exploratory.")
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit typical-case videos for the Health Qigong embodied-analysis layer.")
    parser.add_argument("--manifest", default="data/qigong_video_manifest.csv")
    parser.add_argument("--metadata", default="data/qigong_platform_metadata.csv")
    parser.add_argument("--profile", choices=["formal", "smoke"], default="formal")
    parser.add_argument("--min-cases", type=int, default=3)
    parser.add_argument("--min-existing-local", type=int, default=3)
    parser.add_argument("--output-md", default="runs/qigong_platform/audit/video_manifest_audit.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/audit/video_manifest_audit.json")
    args = parser.parse_args()

    rows = audit(
        manifest_rows=read_rows(Path(args.manifest)),
        metadata_hashes=included_metadata_hashes(Path(args.metadata)),
        formal=args.profile == "formal",
        min_cases=args.min_cases,
        min_existing_local=args.min_existing_local,
    )
    write_outputs(rows, Path(args.output_md), Path(args.output_json))
    print(args.output_md)


if __name__ == "__main__":
    main()
