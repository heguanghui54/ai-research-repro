#!/usr/bin/env python3
"""Audit a qigong manuscript against current formal evidence gates."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Item:
    gate: str
    status: str
    evidence: str
    recommendation: str


def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def status(ok: bool, warn: bool = False) -> str:
    if ok:
        return "pass"
    return "warn" if warn else "fail"


def contains_any(text: str, patterns: list[str]) -> list[str]:
    return [pat for pat in patterns if re.search(pat, text, flags=re.IGNORECASE)]


def unsupported_hits(text: str, patterns: list[str]) -> list[str]:
    hits: list[str] = []
    for pat in patterns:
        for match in re.finditer(pat, text, flags=re.IGNORECASE):
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            context = text[start:end]
            if re.search(r"不能|不可|不得|不报告|不写|尚未|未通过|门槛|只有.*后|当前版本", context):
                continue
            hits.append(pat)
            break
    return hits


def add(items: list[Item], gate: str, ok: bool, evidence: str, recommendation: str, warn: bool = False) -> None:
    items.append(Item(gate, status(ok, warn), evidence, recommendation))


def audit(manuscript: Path) -> list[Item]:
    text = manuscript.read_text(encoding="utf-8") if manuscript.exists() else ""
    web = read_json(ROOT / "runs/qigong_platform/formal_merge/web_coding_submissions_export_summary.json") or {}
    comments = read_json(ROOT / "runs/qigong_platform/formal_merge/qigong_comment_collection_targets.json") or {}
    video = read_json(ROOT / "runs/qigong_platform/formal_merge/video_file_preflight.json") or {}
    ext_refs = read_json(ROOT / "docs/qigong_platform_paper/external_reference_verification_pack.json") or {}
    items: list[Item] = []

    add(items, "manuscript_exists", manuscript.exists(), str(manuscript), "Create the current-evidence manuscript.")
    complete_rows = int(web.get("complete_rows", 0) or 0) if isinstance(web, dict) else 0
    primary_rows = int(web.get("primary_submissions", 0) or 0) if isinstance(web, dict) else 0
    if complete_rows >= 120 and primary_rows >= 120:
        web_state_ok = ("完整提交 0 条" not in text and "主编码提交 0 条" not in text)
        web_rec = "When web coding is complete, manuscript should report audited coding results rather than the old pending state."
    else:
        web_state_ok = "完整提交 0 条" in text and "主编码提交 0 条" in text and "STU01-STU10" in text
        web_rec = "Current draft must state that student web coding has started but has no complete submissions yet."
    add(
        items,
        "web_coding_state_matches_export",
        web_state_ok,
        f"web_summary={web}",
        web_rec,
    )
    add(
        items,
        "comment_state_matches_targets",
        "覆盖 59 个正式样本视频" in text and "仍需补采 447 条" in text,
        f"comment_summary={comments.get('summary', {})}",
        "Use the latest comment target audit: 263 comments, 59/120 covered videos, 447 additional comments needed.",
    )
    outdated_hits = contains_any(
        text,
        [
            r"覆盖\s*101\s*个视频",
            r"覆盖\s*120\s*个正式编码视频，其中已有真实评论预填\s*153\s*行",
        ],
    )
    outdated_hits.extend(unsupported_hits(text, [r"评论.*频率结论"]))
    add(
        items,
        "no_outdated_comment_numbers",
        not outdated_hits,
        "hits=" + json.dumps(outdated_hits, ensure_ascii=False),
        "Remove old comment coverage numbers from prior drafts.",
    )
    sports_risky = contains_any(
        text,
        [
            r"SportsLabKit 环境可用",
            r"SportsLabKit.*实测",
            r"姿态轨迹.*结果",
            r"身体中心.*结果",
            r"动作偏移.*发现",
        ],
    )
    allowed_context = "不能报告姿态轨迹" in text and "SportsLabKit 和 MediaPipe 尚未在当前环境跑通" in text
    add(
        items,
        "sportslabkit_boundary_current",
        (not sports_risky) or allowed_context,
        f"video_summary={video.get('summary', {})}, risky_hits={sports_risky}",
        "Do not write SportsLabKit or pose features as completed evidence before local videos and Ubuntu run pass.",
    )
    add(
        items,
        "external_refs_inserted",
        "Derrida, J. (1976)" in text
        and "MultiSports" in text
        and "SoccerNet-v2" in text
        and "P2ANet" in text
        and len(ext_refs.get("references", [])) >= 13,
        f"external_ref_count={len(ext_refs.get('references', []))}",
        "Current draft should carry the verified external theory/technical/platform reference layer.",
    )
    forbidden = contains_any(text, [r"\bMonica\b", r"AI\s*Scientist", r"api[_ -]?key", r"admin code", r"sk-[A-Za-z0-9]"])
    add(
        items,
        "no_private_or_workflow_terms",
        not forbidden,
        "hits=" + json.dumps(forbidden, ensure_ascii=False),
        "Public manuscript must not expose private model routes, API keys, admin codes, or workflow authorship.",
    )
    add(
        items,
        "author_identity_current",
        "石伟" in text[:1600] and "西南科技大学体育学院" in text[:1600] and "中国科学技术大学博士" in text[:1600],
        "required=石伟/西南科技大学体育学院/中国科学技术大学博士",
        "Keep the user-provided author identity and do not list AI tools as authors.",
    )
    return items


def write(items: list[Item], md: Path, js: Path) -> None:
    md.parent.mkdir(parents=True, exist_ok=True)
    counts = {s: sum(1 for item in items if item.status == s) for s in ["pass", "warn", "fail"]}
    lines = [
        "# 当前证据一致性稿件审计",
        "",
        f"Summary: pass={counts['pass']}, warn={counts['warn']}, fail={counts['fail']}",
        "",
        "| Gate | Status | Evidence | Recommendation |",
        "|---|---|---|---|",
    ]
    for item in items:
        ev = item.evidence.replace("|", "\\|")
        rec = item.recommendation.replace("|", "\\|")
        lines.append(f"| {item.gate} | {item.status} | {ev} | {rec} |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    js.write_text(json.dumps([asdict(item) for item in items], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript", default="docs/qigong_platform_paper/manuscript_draft_v0_8_current_evidence.md")
    parser.add_argument("--output-md", default="runs/qigong_platform/formal_merge/manuscript_v0_8_current_evidence_audit.md")
    parser.add_argument("--output-json", default="runs/qigong_platform/formal_merge/manuscript_v0_8_current_evidence_audit.json")
    args = parser.parse_args()
    items = audit(Path(args.manuscript))
    write(items, ROOT / args.output_md, ROOT / args.output_json)
    print(ROOT / args.output_md)


if __name__ == "__main__":
    main()
