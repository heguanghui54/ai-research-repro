from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from analyze_qigong_comments import LEXICONS


FIELDS = [
    "case_id",
    "video_id",
    "signal_category",
    "matched_terms",
    "comment_excerpt",
    "comment_length",
    "source_position",
    "like_count",
    "use_in_manuscript",
    "interpretive_note",
]

CONTEXT_EXCLUSION_TERMS = [
    "<body>",
    "pending",
    "java程序员需要的计算机网络",
    "操作系统，组成原理课程",
    "句子成分分析的word文档",
    "提取码",
    "壁纸打包",
    "课件的网站",
    "本地运行",
    "他的官网",
    "减肥纱布",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def clean_text(text: str) -> str:
    text = re.sub(r"https?://\S+|www\.\S+", "[URL]", str(text or ""), flags=re.I)
    text = re.sub(r"@[\w\u4e00-\u9fff_-]{2,}", "[MENTION]", text)
    return re.sub(r"\s+", " ", text).strip()


def excerpt(text: str, limit: int) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def int_value(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def category_hits(text: str, category: str) -> list[str]:
    return [term for term in LEXICONS[category] if term in text]


def likely_off_context(text: str) -> bool:
    lowered = text.casefold()
    return any(term.casefold() in lowered for term in CONTEXT_EXCLUSION_TERMS)


def note_for(category: str) -> str:
    notes = {
        "meme_play": "Shows playful recontextualization of Health Qigong in platform vernacular.",
        "embodiment_deferral": "Shows the gap between collecting/watching and embodied practice.",
        "authority_contest": "Shows contestation over standard, teacher authority, or correctness.",
        "health_anxiety": "Shows health-anxiety framing and modern-life pain-point translation.",
        "practice_intention": "Shows practical learning intention and possible re-embodiment.",
        "commercial_suspicion": "Shows suspicion toward platform commerce and course conversion.",
    }
    return notes.get(category, "Supports contextual close reading.")


def select_cases(rows: list[dict[str, str]], *, per_category: int, excerpt_chars: int) -> list[dict[str, str]]:
    candidates: dict[str, list[dict[str, str]]] = {category: [] for category in LEXICONS}
    seen_comment_text: set[str] = set()
    for row in rows:
        text = clean_text(row.get("comment_text", ""))
        if not text:
            continue
        if likely_off_context(text):
            continue
        key = text.casefold()
        if key in seen_comment_text:
            continue
        seen_comment_text.add(key)
        for category in LEXICONS:
            hits = category_hits(text, category)
            if hits:
                item = dict(row)
                item["_clean_text"] = text
                item["_hits"] = ";".join(hits)
                item["_category"] = category
                item["_score"] = len(hits) * 10 + min(int_value(row.get("like_count", "")), 999)
                candidates[category].append(item)

    cases: list[dict[str, str]] = []
    used_video_category: set[tuple[str, str]] = set()
    for category in LEXICONS:
        selected = 0
        for item in sorted(candidates[category], key=lambda row: (-int(row["_score"]), row.get("video_id", ""), row.get("source_position", ""))):
            video_id = item.get("video_id", "")
            if (video_id, category) in used_video_category:
                continue
            used_video_category.add((video_id, category))
            selected += 1
            cases.append(
                {
                    "case_id": f"CR{len(cases) + 1:03d}",
                    "video_id": video_id,
                    "signal_category": category,
                    "matched_terms": item["_hits"],
                    "comment_excerpt": excerpt(item["_clean_text"], excerpt_chars),
                    "comment_length": str(len(item["_clean_text"])),
                    "source_position": item.get("source_position", ""),
                    "like_count": item.get("like_count", ""),
                    "use_in_manuscript": "candidate_contextual_quote",
                    "interpretive_note": note_for(category),
                }
            )
            if selected >= per_category:
                break
    return cases


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in FIELDS} for row in rows)


def write_md(path: Path, rows: list[dict[str, str]], comments_path: str, per_category: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(row["signal_category"] for row in rows)
    lines = [
        "# Comment Close-Reading Cases",
        "",
        "This file selects anonymized public-comment excerpts for contextual close reading. It is not a frequency table and should not be used for prevalence claims.",
        "",
        f"- Source comments: `{comments_path}`",
        f"- Target cases per category: {per_category}",
        f"- Selected cases: {len(rows)}",
        f"- Category counts: {dict(counts)}",
        "",
        "| Case | Video ID | Signal | Matched Terms | Excerpt | Interpretive Use |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        safe_excerpt = row["comment_excerpt"].replace("|", "/")
        lines.append(
            f"| {row['case_id']} | {row['video_id']} | {row['signal_category']} | {row['matched_terms']} | {safe_excerpt} | {row['interpretive_note']} |"
        )
    lines.extend(
        [
            "",
            "## Manuscript Boundary",
            "",
            "- Use these cases as anonymized, short contextual examples in network-ethnographic interpretation.",
            "- Do not infer platform prevalence from this table.",
            "- Pair each selected case with the formal comment audit status when writing results.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Select anonymized Health Qigong comment cases for contextual close reading.")
    parser.add_argument("--comments", default="data/qigong_comments_formal.csv")
    parser.add_argument("--per-category", type=int, default=3)
    parser.add_argument("--excerpt-chars", type=int, default=36)
    parser.add_argument("--output-csv", default="runs/qigong_platform/comments_formal_current/comment_close_reading_cases.csv")
    parser.add_argument("--output-md", default="runs/qigong_platform/comments_formal_current/comment_close_reading_cases.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/comments_formal_current/comment_close_reading_cases.json")
    args = parser.parse_args()

    rows = select_cases(read_csv(Path(args.comments)), per_category=args.per_category, excerpt_chars=args.excerpt_chars)
    write_csv(Path(args.output_csv), rows)
    write_md(Path(args.output_md), rows, args.comments, args.per_category)
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(
        json.dumps({"comments": args.comments, "per_category": args.per_category, "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(args.output_csv)
    print(args.output_md)
    print(args.output_json)


if __name__ == "__main__":
    main()
