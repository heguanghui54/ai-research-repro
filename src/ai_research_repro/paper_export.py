from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def _inline_md_to_tex(text: str) -> str:
    placeholders: list[str] = []

    def stash_code(match: re.Match[str]) -> str:
        placeholders.append(r"\texttt{" + _tex_escape(match.group(1)) + "}")
        return f"@@PLACEHOLDER{len(placeholders) - 1}@@"

    def stash_cite(match: re.Match[str]) -> str:
        keys = [item.strip().lstrip("@") for item in re.split(r"[;,]", match.group(1)) if item.strip()]
        placeholders.append(r"\cite{" + ",".join(keys) + "}")
        return f"@@PLACEHOLDER{len(placeholders) - 1}@@"

    text = re.sub(r"`([^`]+)`", stash_code, text)
    text = re.sub(r"\[((?:@[A-Za-z0-9_:-]+(?:[;,]\s*)?)+)\]", stash_cite, text)
    text = _tex_escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", text)
    for idx, value in enumerate(placeholders):
        text = text.replace(_tex_escape(f"@@PLACEHOLDER{idx}@@"), value)
    return text


def markdown_to_latex(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    in_code = False
    in_itemize = False
    in_table = False
    seen_title = False

    def close_itemize() -> None:
        nonlocal in_itemize
        if in_itemize:
            out.append(r"\end{itemize}")
            in_itemize = False

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            out.append(r"\end{tabular}")
            out.append(r"\end{center}")
            in_table = False

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            close_itemize()
            close_table()
            if in_code:
                out.append(r"\end{verbatim}")
                in_code = False
            else:
                out.append(r"\begin{verbatim}")
                in_code = True
            continue
        if in_code:
            out.append(line)
            continue
        if not line:
            close_itemize()
            close_table()
            out.append("")
            continue
        image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)$", line)
        if image_match:
            close_itemize()
            close_table()
            alt_text = image_match.group(1).strip()
            image_path = image_match.group(2).strip()
            out.extend(
                [
                    r"\begin{figure}[htbp]",
                    r"\centering",
                    r"\includegraphics[width=0.92\linewidth]{\detokenize{" + image_path + "}}",
                    r"\caption{" + _inline_md_to_tex(alt_text) + "}",
                    r"\end{figure}",
                ]
            )
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if set(cells[0]) <= {"-", ":"}:
                continue
            if not in_table:
                close_itemize()
                out.append(r"\begin{center}")
                out.append(r"\begin{tabular}{" + "l" * len(cells) + "}")
                in_table = True
            out.append(" & ".join(_inline_md_to_tex(cell) for cell in cells) + r" \\")
            continue
        close_table()
        if line.startswith("# "):
            close_itemize()
            if not seen_title:
                seen_title = True
            else:
                out.append(r"\section{" + _inline_md_to_tex(line[2:].strip()) + "}")
            continue
        if line.startswith("## "):
            close_itemize()
            out.append(r"\section{" + _inline_md_to_tex(line[3:].strip()) + "}")
            continue
        if line.startswith("### "):
            close_itemize()
            out.append(r"\subsection{" + _inline_md_to_tex(line[4:].strip()) + "}")
            continue
        if line.startswith("- "):
            if not in_itemize:
                out.append(r"\begin{itemize}")
                in_itemize = True
            out.append(r"\item " + _inline_md_to_tex(line[2:].strip()))
            continue
        close_itemize()
        out.append(_inline_md_to_tex(line))

    close_itemize()
    close_table()
    if in_code:
        out.append(r"\end{verbatim}")
    body = "\n".join(out)
    title = "AI Research Reproduction Paper"
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return rf"""\documentclass[11pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{hyperref}}
\usepackage{{booktabs}}
\usepackage{{verbatim}}
\usepackage{{float}}
\title{{{_inline_md_to_tex(title)}}}
\author{{AI Scientist-v2 Reproduction Pipeline}}
\date{{\today}}
\begin{{document}}
\maketitle

{body}

\bibliographystyle{{plain}}
\bibliography{{references}}
\end{{document}}
"""


def export_paper_package(
    *,
    paper_markdown: Path,
    output_dir: Path,
    results_dir: Path | None = None,
    references_path: Path | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_text = paper_markdown.read_text(encoding="utf-8")
    paper_md_out = output_dir / "paper.md"
    paper_tex_out = output_dir / "paper.tex"
    paper_md_out.write_text(markdown_text, encoding="utf-8")
    paper_tex_out.write_text(markdown_to_latex(markdown_text), encoding="utf-8")

    copied: list[str] = [str(paper_md_out), str(paper_tex_out)]
    existing_pdf = output_dir / "paper.pdf"
    if existing_pdf.exists():
        copied.append(str(existing_pdf))
    if references_path and references_path.exists():
        dst = output_dir / "references.bib"
        shutil.copy2(references_path, dst)
        copied.append(str(dst))

    if results_dir and results_dir.exists():
        for name in [
            "analysis.json",
            "analysis.md",
            "claim_audit.json",
            "claim_audit.md",
            "paper_quality_review.json",
            "paper_quality_review.md",
            "artifact_quality_judge.json",
            "artifact_quality_judge.md",
            "artifact_quality_judge_monica.json",
            "artifact_quality_judge_monica.md",
            "artifact_quality_judge_comparison.json",
            "artifact_quality_judge_comparison.md",
            "quality_primary_analysis.json",
            "quality_primary_analysis.md",
            "quality_gap_analysis.json",
            "quality_gap_analysis.md",
            "divergence_analysis.json",
            "divergence_analysis.md",
            "policy_update_analysis.json",
            "policy_update_analysis.md",
            "structured_memory_analysis.json",
            "structured_memory_analysis.md",
            "repro_manifest.json",
            "research_benchmark_summary.csv",
            "research_benchmark_summary.md",
            "role_trace_index.md",
            "figure_critique_monica.md",
        ]:
            src = results_dir / name
            if src.exists():
                dst = output_dir / name
                shutil.copy2(src, dst)
                copied.append(str(dst))
        for folder in ["figures", "figures_png", "role_traces"]:
            src_dir = results_dir / folder
            if src_dir.exists():
                dst_dir = output_dir / folder
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
                copied.append(str(dst_dir))
        supplemental_dir = output_dir / "supplemental"
        supplemental_dir.mkdir(exist_ok=True)
        for src in [
            Path("research_artifacts/reproducibility_checklist.md"),
            Path("research_artifacts/external_tasks_curated.json"),
            Path("research_artifacts/airs_official_tasks_subset.json"),
            Path("research_artifacts/airs_official_tasks_12.json"),
            Path("research_artifacts/ai_research_tasks_20.json"),
        ]:
            if src.exists():
                dst = supplemental_dir / src.name
                shutil.copy2(src, dst)
                copied.append(str(dst))
        for src_dir in [
            Path("runs/research_external_curated_deepseek"),
            Path("runs/airs_official_subset_deepseek"),
            Path("runs/airs_official_12_deepseek"),
            Path("runs/ai_research_tasks20_representative_seed0"),
            Path("runs/ai_research_tasks20_primary_seeds1_2_deepseek"),
            Path("runs/ai_research_tasks20_primary_3seed_deepseek"),
            Path("runs/ai_research_tasks20_primary_seeds3_4_deepseek"),
            Path("runs/ai_research_tasks20_primary_5seed_deepseek"),
            Path("runs/ai_research_tasks20_primary_seed5_deepseek"),
            Path("runs/ai_research_tasks20_primary_seed6_deepseek"),
            Path("runs/ai_research_tasks20_primary_seed7_deepseek"),
            Path("runs/ai_research_tasks20_primary_seed8_deepseek"),
            Path("runs/ai_research_tasks20_primary_seed9_deepseek"),
            Path("runs/ai_research_tasks20_primary_8seed_deepseek"),
            Path("runs/ai_research_tasks20_primary_10seed_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed0_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed1_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed2_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed3_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed4_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed5_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed6_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed7_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed8_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_seed9_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_3seed_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_5seed_deepseek"),
            Path("runs/ai_research_tasks20_self_consistency_10seed_deepseek"),
            Path("runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_3seed_deepseek"),
            Path("runs/ai_research_tasks20_primary_10seed_plus_selfconsistency_10seed_deepseek"),
            Path("runs/ai_research_tasks20_monica_gpt4o_seed0"),
            Path("runs/ai_research_tasks20_monica_gpt4o_seeds1_2"),
            Path("runs/ai_research_tasks20_monica_gpt4o_3seed"),
            Path("runs/research_pilot_monica_gpt4o_seed0"),
            Path("runs/research_role_ablation_deepseek_seed0"),
            Path("runs/airs_evaluator_smoke_svamp"),
            Path("runs/airs_svamp_deepseek_submission"),
            Path("research_artifacts/human_eval_20task_packet"),
        ]:
            if not src_dir.exists():
                continue
            dst_dir = supplemental_dir / src_dir.name
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(
                src_dir,
                dst_dir,
                ignore=shutil.ignore_patterns("submission_package"),
            )
            copied.append(str(dst_dir))
        code_dir = supplemental_dir / "code_snapshot"
        if code_dir.exists():
            shutil.rmtree(code_dir)
        code_dir.mkdir()
        for src_dir in [Path("src"), Path("scripts")]:
            if src_dir.exists():
                shutil.copytree(
                    src_dir,
                    code_dir / src_dir.name,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
                )
        for src_file in [Path("pyproject.toml"), Path("requirements.txt"), Path(".env.example"), Path("README.md")]:
            if src_file.exists():
                shutil.copy2(src_file, code_dir / src_file.name)
        copied.append(str(code_dir))

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "paper_markdown": str(paper_markdown),
        "results_dir": str(results_dir) if results_dir else "",
        "files": copied,
        "notes": [
            "Compile paper.tex with a local LaTeX distribution if PDF output is needed.",
            "Do not claim final empirical results unless claim_audit.md is clean and runs are API-backed.",
        ],
    }
    manifest_path = output_dir / "package_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    copied.append(str(manifest_path))
    return {"output_dir": str(output_dir), "manifest": str(manifest_path), "files": copied}
