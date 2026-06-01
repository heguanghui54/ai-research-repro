from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


REQUIRED_EXTERNAL_LAYERS = [
    {
        "layer": "core_theory",
        "target": "Derrida/deconstruction primary or authoritative Chinese translation",
        "minimum": 2,
        "paper_use": "延异、踪迹、补充、书写、二元对立解构的理论来源",
        "verification_rule": "以正式出版图书或权威译本为准；核对译名、出版年、出版社、页码。",
    },
    {
        "layer": "sports_video_benchmark",
        "target": "MultiSports / SoccerNet / P2ANet / sports action localization papers",
        "minimum": 3,
        "paper_use": "说明体育视频动作定位、时空标注、姿态/追踪工具的技术背景",
        "verification_rule": "优先核对论文 DOI/arXiv、会议/期刊、官方 GitHub 或 dataset page；不得写成健身气功数据集。",
    },
    {
        "layer": "tool_method",
        "target": "SportsLabKit / OpenCV / MediaPipe or actual fallback tool references",
        "minimum": 2,
        "paper_use": "支撑视频特征提取、姿态/运动/镜头变化分析方法",
        "verification_rule": "只引用实际使用过的工具；若最终未用 SportsLabKit，不得把后备链路写成 SportsLabKit 结果。",
    },
    {
        "layer": "platform_health_communication",
        "target": "短视频/平台健康传播、健身短视频、算法可见性与社交媒体健康传播文献",
        "minimum": 3,
        "paper_use": "连接体育短视频传播、健康话语、平台可见性和用户互动",
        "verification_rule": "优先选择近五年同行评审文献；核对 DOI、期刊名、页码。",
    },
]


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def key(row: dict[str, str]) -> str:
    return clean(row.get("title"))


def has_core_bibliography(row: dict[str, str]) -> bool:
    return all(clean(row.get(field)) for field in ["authors", "title", "journal", "year", "volume", "issue", "pages", "doi"])


def build_rows(shortlist: list[dict[str, str]], catalog: list[dict[str, str]]) -> list[dict[str, str]]:
    catalog_by_title = {key(row): row for row in catalog if key(row)}
    rows: list[dict[str, str]] = []
    for index, item in enumerate(shortlist, start=1):
        title = key(item)
        catalog_row = catalog_by_title.get(title, {})
        in_catalog = bool(catalog_row)
        source = catalog_row or item
        missing = [field for field in ["authors", "journal", "year", "volume", "issue", "pages", "doi"] if not clean(source.get(field))]
        rows.append(
            {
                "rank": str(index),
                "title": title,
                "authors": clean(source.get("authors")),
                "journal": clean(source.get("journal")),
                "year": clean(source.get("year")),
                "volume": clean(source.get("volume")),
                "issue": clean(source.get("issue")),
                "pages": clean(source.get("pages")),
                "doi": clean(source.get("doi")),
                "primary_category": clean(item.get("primary_category")),
                "categories": clean(item.get("categories")),
                "section_hint": clean(item.get("section_hint")),
                "in_catalog_matrix": str(in_catalog).lower(),
                "has_cnki_link": str(bool(clean(source.get("link")))).lower(),
                "core_bibliography_complete": str(not missing).lower(),
                "missing_fields": ";".join(missing),
                "verification_status": "catalog_metadata_ready" if in_catalog and not missing else "needs_manual_verification",
                "verification_note": "Still verify against CNKI/journal page before final submission.",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else [
        "rank",
        "title",
        "authors",
        "journal",
        "year",
        "volume",
        "issue",
        "pages",
        "doi",
        "primary_category",
        "categories",
        "section_hint",
        "in_catalog_matrix",
        "has_cnki_link",
        "core_bibliography_complete",
        "missing_fields",
        "verification_status",
        "verification_note",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def ref_text(row: dict[str, str]) -> str:
    return (
        f"{row['authors']}. {row['title']}[J]. {row['journal']}, "
        f"{row['year']}, {row['volume']}({row['issue']}):{row['pages']}. DOI:{row['doi']}"
    )


def write_md(path: Path, rows: list[dict[str, str]], external_layers: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["verification_status"] for row in rows)
    category_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        for category in clean(row.get("categories")).split(";"):
            if category:
                category_counts[category] += 1

    lines = [
        "# 投稿前参考文献核验包",
        "",
        "本文件把目标刊题录矩阵中的候选文献与外部理论/技术文献分层处理。它不是最终参考文献表；正式投稿前仍需逐条核对 CNKI、期刊官网或出版社元数据。",
        "",
        "## 目标刊候选文献状态",
        "",
        f"- 候选条目: {len(rows)}",
        f"- catalog_metadata_ready: {status_counts.get('catalog_metadata_ready', 0)}",
        f"- needs_manual_verification: {status_counts.get('needs_manual_verification', 0)}",
        "",
        "## 目标刊分类覆盖",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for category, count in sorted(category_counts.items()):
        lines.append(f"| {category} | {count} |")

    lines.extend(
        [
            "",
            "## 可优先进入初稿的目标刊文献",
            "",
            "以下条目已能从本地题录矩阵反查到作者、题名、期刊、年卷期页和 DOI，但最终仍需投稿前人工核验。",
            "",
        ]
    )
    ready = [row for row in rows if row["verification_status"] == "catalog_metadata_ready"]
    for index, row in enumerate(ready[:20], start=1):
        lines.append(f"{index}. {ref_text(row)}")
        lines.append(f"   - 用途：{row['section_hint']}")
    if len(ready) > 20:
        lines.append(f"- 其余 {len(ready) - 20} 条见 CSV。")

    needs = [row for row in rows if row["verification_status"] != "catalog_metadata_ready"]
    lines.extend(["", "## 仍需人工核验的目标刊候选", ""])
    if not needs:
        lines.append("- 暂无。")
    for row in needs:
        lines.append(f"- {row['title']}：missing={row['missing_fields'] or 'unknown'}")

    lines.extend(["", "## 外部理论与技术文献缺口", ""])
    lines.append("| Layer | Minimum | Target | Paper Use | Verification Rule |")
    lines.append("|---|---:|---|---|---|")
    for item in external_layers:
        lines.append(
            f"| {item['layer']} | {item['minimum']} | {item['target']} | {item['paper_use']} | {item['verification_rule']} |"
        )

    lines.extend(
        [
            "",
            "## 写作规则",
            "",
            "- 目标刊文献用于建立与《武汉体育学院学报》的直接对话。",
            "- 德里达与媒介理论只服务于变量化解释，不把论文写成纯哲学文章。",
            "- MultiSports、P2ANet、SportsLabKit 等技术文献只进入方法和工具边界，不支持健身气功平台传播意义结论。",
            "- 未核验 DOI、卷期页和出版信息的条目不得进入投稿版参考文献表。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a pre-submission reference verification pack for the Health Qigong paper.")
    parser.add_argument("--shortlist", default="docs/qigong_platform_paper/reference_shortlist.csv")
    parser.add_argument("--catalog", default="docs/qigong_platform_paper/wuhan_catalog_reference_matrix.csv")
    parser.add_argument("--output-csv", default="docs/qigong_platform_paper/reference_verification_pack.csv")
    parser.add_argument("--output-md", default="docs/qigong_platform_paper/reference_verification_pack.md")
    parser.add_argument("--output-json", default="docs/qigong_platform_paper/reference_verification_pack.json")
    args = parser.parse_args()

    rows = build_rows(read_csv(Path(args.shortlist)), read_csv(Path(args.catalog)))
    write_csv(Path(args.output_csv), rows)
    write_md(Path(args.output_md), rows, REQUIRED_EXTERNAL_LAYERS)
    payload = {
        "target_journal_rows": rows,
        "external_layers": REQUIRED_EXTERNAL_LAYERS,
        "summary": {
            "target_journal_rows": len(rows),
            "catalog_metadata_ready": sum(1 for row in rows if row["verification_status"] == "catalog_metadata_ready"),
            "needs_manual_verification": sum(1 for row in rows if row["verification_status"] != "catalog_metadata_ready"),
        },
    }
    Path(args.output_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output_md)
    print(args.output_csv)
    print(args.output_json)


if __name__ == "__main__":
    main()
