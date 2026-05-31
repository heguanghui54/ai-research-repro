from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DDL = """
create extension if not exists pgcrypto;

create table if not exists public.coding_videos (
  video_id text primary key,
  priority integer not null,
  platform text not null,
  keyword text,
  title text,
  hashtags text,
  duration_sec numeric,
  like_count numeric,
  comment_count numeric,
  url_hash text,
  video_url text,
  link_status text not null default 'missing_private_url',
  suggested jsonb not null default '{}'::jsonb,
  llm_rationale text,
  primary_student integer not null,
  double_student integer,
  batch_no integer not null,
  created_at timestamptz not null default now()
);

create table if not exists public.coding_submissions (
  id uuid primary key default gen_random_uuid(),
  video_id text not null references public.coding_videos(video_id) on delete cascade,
  student_code text not null,
  student_name text not null,
  task_role text not null default 'primary',
  watched boolean not null default false,
  video_access_status text not null default 'opened',
  dominant_frame text not null,
  body_visibility text not null,
  movement_tempo text not null,
  origin_reference text not null,
  supplement_mode text not null,
  binary_reversal text not null,
  visibility_centrality text not null,
  tempo_discipline text not null,
  efficacy_tagging text not null,
  image_trace_strength text not null,
  media_temporality text not null,
  meme_density text not null,
  embodied_dissolution text not null,
  trace_markers text,
  notes text,
  submitted_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(video_id, student_code, task_role)
);

alter table public.coding_videos enable row level security;
alter table public.coding_submissions enable row level security;

drop policy if exists "coding_videos_read_for_web" on public.coding_videos;
create policy "coding_videos_read_for_web"
on public.coding_videos for select
to anon
using (true);

drop policy if exists "coding_submissions_select_for_web" on public.coding_submissions;
create policy "coding_submissions_select_for_web"
on public.coding_submissions for select
to anon
using (true);

drop policy if exists "coding_submissions_insert_for_web" on public.coding_submissions;
create policy "coding_submissions_insert_for_web"
on public.coding_submissions for insert
to anon
with check (true);

drop policy if exists "coding_submissions_update_for_web" on public.coding_submissions;
create policy "coding_submissions_update_for_web"
on public.coding_submissions for update
to anon
using (true)
with check (true);

grant usage on schema public to anon;
grant select on public.coding_videos to anon;
grant select, insert, update on public.coding_submissions to anon;
"""


SUGGESTION_FIELDS = [
    "suggested_dominant_frame",
    "suggested_body_visibility",
    "suggested_movement_tempo",
    "suggested_origin_reference",
    "suggested_supplement_mode",
    "suggested_binary_reversal",
    "suggested_visibility_centrality",
    "suggested_tempo_discipline",
    "suggested_efficacy_tagging",
    "suggested_image_trace_strength",
    "suggested_media_temporality",
    "suggested_meme_density",
    "suggested_embodied_dissolution",
]


def clean(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def sql_text(value: object) -> str:
    text = clean(value)
    if not text:
        return "null"
    return "'" + text.replace("'", "''") + "'"


def sql_number(value: object) -> str:
    text = clean(value)
    if not text:
        return "null"
    try:
        float(text)
    except ValueError:
        return "null"
    return text


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build_insert(rows: list[dict[str, str]]) -> str:
    return "\n".join(build_insert_chunks(rows, chunk_size=len(rows)))


def build_insert_chunks(rows: list[dict[str, str]], chunk_size: int = 40) -> list[str]:
    chunks: list[str] = []
    for chunk_start in range(0, len(rows), chunk_size):
        chunk_rows = rows[chunk_start : chunk_start + chunk_size]
        chunks.append(build_insert_chunk(chunk_rows, offset=chunk_start))
    return chunks


def build_insert_chunk(rows: list[dict[str, str]], *, offset: int) -> str:
    values = []
    for local_index, row in enumerate(rows, start=1):
        index = offset + local_index
        suggested = {field.replace("suggested_", ""): clean(row.get(field)) for field in SUGGESTION_FIELDS if clean(row.get(field))}
        primary_student = ((index - 1) % 10) + 1
        # A small double-coding subset: every fifth row is assigned to another student.
        double_student = ((primary_student + 4 - 1) % 10) + 1 if index <= 30 and index % 5 == 0 else None
        batch_no = ((index - 1) // 10) + 1
        values.append(
            "("
            + ", ".join(
                [
                    sql_text(row.get("video_id")),
                    str(index),
                    sql_text(row.get("platform")),
                    sql_text(row.get("keyword")),
                    sql_text(row.get("title")),
                    sql_text(row.get("hashtags")),
                    sql_number(row.get("duration_sec")),
                    sql_number(row.get("like_count")),
                    sql_number(row.get("comment_count")),
                    sql_text(row.get("url_hash")),
                    sql_text(row.get("video_url")),
                    sql_text(row.get("link_status") or "missing_private_url"),
                    sql_text(json.dumps(suggested, ensure_ascii=False)) + "::jsonb",
                    sql_text(row.get("llm_rationale")),
                    str(primary_student),
                    "null" if double_student is None else str(double_student),
                    str(batch_no),
                ]
            )
            + ")"
        )
    return (
        """
insert into public.coding_videos (
  video_id, priority, platform, keyword, title, hashtags,
  duration_sec, like_count, comment_count, url_hash, video_url, link_status,
  suggested, llm_rationale, primary_student, double_student, batch_no
) values
"""
        + ",\n".join(values)
        + """
on conflict (video_id) do update set
  priority = excluded.priority,
  platform = excluded.platform,
  keyword = excluded.keyword,
  title = excluded.title,
  hashtags = excluded.hashtags,
  duration_sec = excluded.duration_sec,
  like_count = excluded.like_count,
  comment_count = excluded.comment_count,
  url_hash = excluded.url_hash,
  video_url = excluded.video_url,
  link_status = excluded.link_status,
  suggested = excluded.suggested,
  llm_rationale = excluded.llm_rationale,
  primary_student = excluded.primary_student,
  double_student = excluded.double_student,
  batch_no = excluded.batch_no;
"""
    )


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    by_student = {f"STU{i:02d}": 0 for i in range(1, 11)}
    linked = 0
    for index, row in enumerate(rows, start=1):
        by_student[f"STU{((index - 1) % 10) + 1:02d}"] += 1
        if clean(row.get("video_url")):
            linked += 1
    summary = {
        "rows": len(rows),
        "linked_rows": linked,
        "missing_link_rows": len(rows) - linked,
        "primary_tasks_by_student": by_student,
        "double_check_rule": "Rows 5,10,15,20,25,30 are assigned to a second student offset by +4.",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Supabase schema and seed SQL for the Health Qigong coding web app.")
    parser.add_argument("--input", default="data/private/qigong_120_coding_export_template_with_links.csv")
    parser.add_argument("--schema-sql", default="runs/qigong_platform/formal_merge/coding_web_schema.sql")
    parser.add_argument("--seed-sql", default="runs/qigong_platform/formal_merge/coding_web_seed.sql")
    parser.add_argument("--seed-chunk-dir", default="runs/qigong_platform/formal_merge/coding_web_seed_chunks")
    parser.add_argument("--summary-json", default="runs/qigong_platform/formal_merge/coding_web_seed_summary.json")
    args = parser.parse_args()

    rows = read_csv(Path(args.input))
    Path(args.schema_sql).parent.mkdir(parents=True, exist_ok=True)
    Path(args.schema_sql).write_text(DDL.strip() + "\n", encoding="utf-8")
    seed_prefix = "delete from public.coding_submissions;\ndelete from public.coding_videos;\n\n"
    Path(args.seed_sql).write_text(seed_prefix + build_insert(rows), encoding="utf-8")
    chunk_dir = Path(args.seed_chunk_dir)
    chunk_dir.mkdir(parents=True, exist_ok=True)
    for old_chunk in chunk_dir.glob("seed_chunk_*.sql"):
        old_chunk.unlink()
    for index, chunk in enumerate(build_insert_chunks(rows), start=1):
        prefix = seed_prefix if index == 1 else ""
        (chunk_dir / f"seed_chunk_{index:02d}.sql").write_text(prefix + chunk, encoding="utf-8")
    write_summary(Path(args.summary_json), rows)
    print(args.schema_sql)
    print(args.seed_sql)
    print(args.summary_json)


if __name__ == "__main__":
    main()
