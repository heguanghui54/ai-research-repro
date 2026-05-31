from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


CORE_FIELDS = [
    "dominant_frame",
    "body_visibility",
    "movement_tempo",
    "origin_reference",
    "supplement_mode",
    "binary_reversal",
    "visibility_centrality",
    "tempo_discipline",
    "efficacy_tagging",
    "image_trace_strength",
    "media_temporality",
    "meme_density",
    "embodied_dissolution",
    "coder_id",
]

CONTENT_FIELDS = [field for field in CORE_FIELDS if field != "coder_id"]

DOUBLE_CODING_MIN_ROWS = 24


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def clean(value: object) -> str:
    return str(value or "").strip()


def get_video_id(row: dict[str, str]) -> str:
    return clean(row.get("video_id") or row.get("\ufeffvideo_id"))


def is_filled(row: dict[str, str], fields: list[str]) -> bool:
    return all(clean(row.get(field)) for field in fields)


def completion_count(row: dict[str, str], fields: list[str]) -> int:
    return sum(1 for field in fields if clean(row.get(field)))


def read_task_summary(task_dir: Path) -> dict[str, object]:
    summary_path = task_dir / "coding_task_pack_summary.json"
    if not summary_path.exists():
        return {"exists": False, "task_files": []}
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    payload["exists"] = True
    return payload


def task_file_progress(task_dir: Path) -> list[dict[str, object]]:
    progress: list[dict[str, object]] = []
    for path in sorted(task_dir.glob("*_coding_tasks.csv")):
        rows = read_csv(path)
        filled = sum(1 for row in rows if is_filled(row, CORE_FIELDS))
        partial = sum(1 for row in rows if completion_count(row, CONTENT_FIELDS) > 0 and not is_filled(row, CORE_FIELDS))
        progress.append(
            {
                "task_file": str(path),
                "rows": len(rows),
                "fully_filled": filled,
                "partial": partial,
                "blank": len(rows) - filled - partial,
            }
        )
    return progress


def make_priority_queue(rows: list[dict[str, str]], *, batch_size: int) -> list[dict[str, object]]:
    queue: list[dict[str, object]] = []
    for row in rows:
        missing = [field for field in CORE_FIELDS if not clean(row.get(field))]
        if not missing:
            continue
        video_id = get_video_id(row)
        queue.append(
            {
                "priority": len(queue) + 1,
                "video_id": video_id,
                "platform": clean(row.get("platform")),
                "keyword": clean(row.get("keyword")),
                "title": clean(row.get("title"))[:120],
                "missing_core_fields": ";".join(missing),
                "missing_count": len(missing),
                "suggested_batch": ((len(queue)) // batch_size) + 1,
            }
        )
    return queue


def gate(status: str, evidence: str, next_action: str) -> dict[str, str]:
    return {"status": status, "evidence": evidence, "next_action": next_action}


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    coding_path = Path(args.coding)
    coding_rows = read_csv(coding_path)
    total = len(coding_rows)
    fully_filled = sum(1 for row in coding_rows if is_filled(row, CORE_FIELDS))
    partial = sum(1 for row in coding_rows if completion_count(row, CORE_FIELDS) > 0 and not is_filled(row, CORE_FIELDS))
    blank = total - fully_filled - partial
    field_completion = {
        field: (sum(1 for row in coding_rows if clean(row.get(field))) / total if total else 0.0)
        for field in CORE_FIELDS
    }
    low_fields = {field: round(rate, 3) for field, rate in field_completion.items() if rate < 1.0}
    platform_counts = Counter(clean(row.get("platform")) or "missing" for row in coding_rows)
    keyword_counts = Counter(clean(row.get("keyword")) or "missing" for row in coding_rows)
    coder_counts = Counter(clean(row.get("coder_id")) or "missing" for row in coding_rows)

    double_a = read_csv(Path(args.double_coder_a))
    double_b = read_csv(Path(args.double_coder_b))
    double_a_filled = sum(1 for row in double_a if is_filled(row, CORE_FIELDS))
    double_b_filled = sum(1 for row in double_b if is_filled(row, CORE_FIELDS))
    double_ready = min(double_a_filled, double_b_filled)

    task_dir = Path(args.task_dir)
    task_summary = read_task_summary(task_dir)
    task_progress = task_file_progress(task_dir)
    priority_queue = make_priority_queue(coding_rows, batch_size=args.batch_size)

    gates = {
        "coding_sheet": gate(
            "pass" if total >= args.target_rows else "fail",
            f"rows={total}, target={args.target_rows}",
            "Keep the formal 120-row coding sample stable unless the sampling plan changes.",
        ),
        "core_field_completion": gate(
            "pass" if fully_filled >= args.target_rows else "fail",
            f"fully_filled={fully_filled}/{args.target_rows}, partial={partial}, blank={blank}, low_fields={low_fields}",
            "Complete all core fields in the formal coding sheet before generating result tables.",
        ),
        "double_coding_progress": gate(
            "pass" if double_ready >= DOUBLE_CODING_MIN_ROWS else "fail",
            f"coder_a_filled={double_a_filled}, coder_b_filled={double_b_filled}, ready_pairs={double_ready}, target={DOUBLE_CODING_MIN_ROWS}",
            "Fill the independent double-coding subset before reliability analysis.",
        ),
        "task_pack": gate(
            "pass" if task_summary.get("exists") and task_progress else "warn",
            f"summary_exists={bool(task_summary.get('exists'))}, task_files={len(task_progress)}",
            "For the first 20 rows, use the private linked HTML workbench first; then ingest the exported CSV and rerun this dashboard.",
        ),
    }
    return {
        "coding": str(coding_path),
        "target_rows": args.target_rows,
        "batch_size": args.batch_size,
        "summary": {
            "total_rows": total,
            "fully_filled": fully_filled,
            "partial": partial,
            "blank": blank,
            "remaining": max(0, args.target_rows - fully_filled),
            "field_completion": {field: round(rate, 3) for field, rate in field_completion.items()},
            "platform_counts": dict(platform_counts),
            "keyword_counts": dict(keyword_counts),
            "coder_counts": dict(coder_counts),
        },
        "double_coding": {
            "coder_a_rows": len(double_a),
            "coder_b_rows": len(double_b),
            "coder_a_filled": double_a_filled,
            "coder_b_filled": double_b_filled,
            "ready_pairs": double_ready,
            "target_pairs": DOUBLE_CODING_MIN_ROWS,
        },
        "task_progress": task_progress,
        "gates": gates,
        "priority_queue": priority_queue,
    }


def write_md(path: Path, payload: dict[str, object], *, queue_csv: str) -> None:
    summary = payload["summary"]
    gates = payload["gates"]
    double = payload["double_coding"]
    task_progress = payload["task_progress"]
    field_completion = summary["field_completion"]
    priority_queue = payload["priority_queue"]
    gate_counts = Counter(gate_data["status"] for gate_data in gates.values())
    lines = [
        "# Health Qigong Human Coding Progress",
        "",
        "This dashboard tracks the formal human-coding bottleneck. It is a workflow artifact, not an empirical result.",
        "",
        f"Summary: pass={gate_counts.get('pass', 0)}, warn={gate_counts.get('warn', 0)}, fail={gate_counts.get('fail', 0)}",
        "",
        "## Current Completion",
        "",
        f"- Coding sheet: `{payload['coding']}`",
        f"- Rows: {summary['total_rows']}",
        f"- Fully filled core rows: {summary['fully_filled']} / {payload['target_rows']}",
        f"- Partial rows: {summary['partial']}",
        f"- Blank rows: {summary['blank']}",
        f"- Remaining formal rows: {summary['remaining']}",
        f"- Priority queue CSV: `{queue_csv}`",
        "",
        "## Gates",
        "",
        "| Gate | Status | Evidence | Next Action |",
        "|---|---|---|---|",
    ]
    for name, gate_data in gates.items():
        lines.append(f"| {name} | {gate_data['status']} | {gate_data['evidence']} | {gate_data['next_action']} |")
    lines.extend(["", "## Field Completion", "", "| Field | Completion |", "|---|---:|"])
    for field, rate in field_completion.items():
        lines.append(f"| {field} | {rate:.3f} |")
    lines.extend(
        [
            "",
            "## Double Coding",
            "",
            f"- Coder A filled: {double['coder_a_filled']} / {double['coder_a_rows']}",
            f"- Coder B filled: {double['coder_b_filled']} / {double['coder_b_rows']}",
            f"- Ready pairs: {double['ready_pairs']} / {double['target_pairs']}",
            "",
            "## Task Files",
            "",
            "| Task File | Rows | Fully Filled | Partial | Blank |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for item in task_progress:
        lines.append(f"| `{item['task_file']}` | {item['rows']} | {item['fully_filled']} | {item['partial']} | {item['blank']} |")
    lines.extend(
        [
            "",
            "## Next Batch Preview",
            "",
            "| Priority | Video ID | Platform | Keyword | Missing Core Fields | Title |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for row in priority_queue[:20]:
        title = str(row["title"]).replace("|", " ")
        lines.append(
            f"| {row['priority']} | {row['video_id']} | {row['platform']} | {row['keyword']} | {row['missing_core_fields']} | {title} |"
        )
    lines.extend(
        [
            "",
            "## First-20 Private Workbench",
            "",
            "- Preferred entry for the first 20 rows: `data/private/qigong_first20_coding_workbench_with_links.html`",
            "- Missing-link TODO: `data/private/qigong_first20_missing_video_links_todo.csv`",
            "- Rule: watch the linked video before coding; rows without a usable link should remain pending until manually verified.",
            "",
            "## Recommended Command Chain",
            "",
            "For the browser workbench export:",
            "",
            "```bash",
            "python scripts/ingest_qigong_first20_export.py",
            "python scripts/build_qigong_human_coding_progress.py",
            "```",
            "",
            "For the full Excel workbook:",
            "",
            "```bash",
            "python scripts/audit_qigong_human_coding_xlsx.py --workbook runs/qigong_platform/formal_merge/qigong_human_coding_workbook.xlsx",
            "python scripts/ingest_qigong_human_coding_xlsx.py --workbook runs/qigong_platform/formal_merge/qigong_human_coding_workbook.xlsx",
            "python scripts/audit_qigong_coding_values.py --coding runs/qigong_platform/formal_merge/qigong_human_coding_from_xlsx.csv --profile formal",
            "python scripts/analyze_qigong_coding.py --coding runs/qigong_platform/formal_merge/double_coding_from_xlsx_coder_a.csv --coder-b runs/qigong_platform/formal_merge/double_coding_from_xlsx_coder_b.csv --output-dir runs/qigong_platform/analysis",
            "python scripts/build_qigong_human_coding_progress.py",
            "```",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a progress dashboard for Health Qigong formal human coding.")
    parser.add_argument("--coding", default="data/qigong_short_video_coding_sheet_formal.csv")
    parser.add_argument("--task-dir", default="runs/qigong_platform/formal_merge/coding_tasks")
    parser.add_argument("--double-coder-a", default="runs/qigong_platform/formal_merge/double_coding_from_xlsx_coder_a.csv")
    parser.add_argument("--double-coder-b", default="runs/qigong_platform/formal_merge/double_coding_from_xlsx_coder_b.csv")
    parser.add_argument("--target-rows", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/human_coding_progress_dashboard.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/human_coding_progress_dashboard.json")
    parser.add_argument("--output-queue", default="runs/qigong_platform/formal_merge/human_coding_next_batches.csv")
    args = parser.parse_args()

    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    queue_fields = ["priority", "video_id", "platform", "keyword", "title", "missing_core_fields", "missing_count", "suggested_batch"]
    write_csv(Path(args.output_queue), payload["priority_queue"], queue_fields)
    write_md(Path(args.output_md), payload, queue_csv=args.output_queue)
    print(args.output_md)
    print(args.output_json)
    print(args.output_queue)


if __name__ == "__main__":
    main()
