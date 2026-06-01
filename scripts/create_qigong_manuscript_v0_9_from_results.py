#!/usr/bin/env python3
"""Assemble a v0.9 manuscript by inserting a gated result brief."""

from __future__ import annotations

import argparse
from pathlib import Path


def insert_result_section(draft: str, brief: str) -> str:
    marker = "## 9 实践路向：健身气功短视频高质量传播"
    if marker not in draft:
        return draft.rstrip() + "\n\n---\n\n" + brief.strip() + "\n"
    before, after = draft.split(marker, 1)
    return before.rstrip() + "\n\n" + brief.strip() + "\n\n" + marker + after


def main() -> None:
    parser = argparse.ArgumentParser(description="Insert the v0.9 result brief into the current-evidence qigong manuscript.")
    parser.add_argument("--draft", default="docs/qigong_platform_paper/manuscript_draft_v0_8_current_evidence.md")
    parser.add_argument("--brief", default="runs/qigong_platform/formal_merge/manuscript_result_brief_v0_9.md")
    parser.add_argument("--output", default="docs/qigong_platform_paper/manuscript_draft_v0_9_gated_results.md")
    args = parser.parse_args()

    draft = Path(args.draft).read_text(encoding="utf-8")
    brief = Path(args.brief).read_text(encoding="utf-8") if Path(args.brief).exists() else "## 5 结果回填状态：结果简报缺失\n"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(insert_result_section(draft, brief), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
