#!/usr/bin/env python3
"""Build school-expert ready extensions for the blind review packet.

The original packet already prepares six text A/B pairs. This script adds a
coordinator-facing recruitment/ethics layer and blinded PDF pairs for the three
deep regeneration cases, so a school or NUS expert-review pilot can be launched
without exposing condition names to reviewers.
"""

from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
PACKET_DIR = DOC_DIR / "experiments" / "human_expert_blind_review_packet_20260602_143000"
PDF_SOURCE_DIR = DOC_DIR / "build" / "deep_regeneration_cases"
PDF_PAIR_DIR = PACKET_DIR / "deep_pdf_pairs"


DEEP_PDF_CASES = [
    {
        "deep_pair_id": "deep_pair_01",
        "paper_id": "openreview_sample_1",
        "title": "Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback",
        "a_condition": "six_gate_hybrid",
        "a_source": "openreview_sample_1_llm_refusal_and_reliability_six_gate_hybrid.pdf",
        "b_condition": "raw_review_guided",
        "b_source": "openreview_sample_1_llm_refusal_and_reliability_review_guided.pdf",
    },
    {
        "deep_pair_id": "deep_pair_02",
        "paper_id": "openreview_sample_2",
        "title": "Forked Diffusion for Conditional Graph Generation",
        "a_condition": "raw_review_guided",
        "a_source": "openreview_sample_2_conditional_graph_generation_and_molecular_design_review_guided.pdf",
        "b_condition": "six_gate_hybrid",
        "b_source": "openreview_sample_2_conditional_graph_generation_and_molecular_design_six_gate_hybrid.pdf",
    },
    {
        "deep_pair_id": "deep_pair_03",
        "paper_id": "openreview_sample_17",
        "title": "Knowledge Unlearning for Mitigating Privacy Risks in Language Models",
        "a_condition": "six_gate_hybrid",
        "a_source": "openreview_sample_17_knowledge_unlearning_and_privacy_risk_six_gate_hybrid.pdf",
        "b_condition": "raw_review_guided",
        "b_source": "openreview_sample_17_knowledge_unlearning_and_privacy_risk_review_guided.pdf",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_pdf_pairs() -> list[dict[str, object]]:
    PDF_PAIR_DIR.mkdir(parents=True, exist_ok=True)
    pairs: list[dict[str, object]] = []
    for item in DEEP_PDF_CASES:
        a_dest = PDF_PAIR_DIR / f"{item['deep_pair_id']}_A.pdf"
        b_dest = PDF_PAIR_DIR / f"{item['deep_pair_id']}_B.pdf"
        shutil.copy2(PDF_SOURCE_DIR / str(item["a_source"]), a_dest)
        shutil.copy2(PDF_SOURCE_DIR / str(item["b_source"]), b_dest)
        pairs.append(
            {
                "deep_pair_id": item["deep_pair_id"],
                "paper_id": item["paper_id"],
                "title": item["title"],
                "reviewer_visible_files": [_rel(a_dest), _rel(b_dest)],
                "condition_key": {
                    "A": item["a_condition"],
                    "A_source": _rel(PDF_SOURCE_DIR / str(item["a_source"])),
                    "B": item["b_condition"],
                    "B_source": _rel(PDF_SOURCE_DIR / str(item["b_source"])),
                },
                "bytes": {"A": a_dest.stat().st_size, "B": b_dest.stat().st_size},
            }
        )
    return pairs


def main() -> None:
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    pairs = build_pdf_pairs()

    hidden_key = {
        "status": "hidden_from_reviewers",
        "purpose": "Map anonymized deep PDF A/B files to raw-review-guided and six-gate-hybrid conditions.",
        "pairs": [
            {
                "deep_pair_id": item["deep_pair_id"],
                "paper_id": item["paper_id"],
                "title": item["title"],
                "A": item["condition_key"]["A"],
                "A_source": item["condition_key"]["A_source"],
                "B": item["condition_key"]["B"],
                "B_source": item["condition_key"]["B_source"],
            }
            for item in pairs
        ],
    }
    (PACKET_DIR / "deep_pdf_condition_key.json").write_text(
        json.dumps(hidden_key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    reviewer_index = [
        "# Optional Deep-Case PDF Appendix For Reviewers",
        "",
        "These PDFs are optional A/B mini-paper artifacts for the three deep",
        "regeneration case studies. The filenames are anonymized and do not reveal",
        "which condition produced each artifact.",
        "",
        "Score them only if the coordinator asks you to complete the optional PDF",
        "appendix. Use the same 1-5 rubric as the main text packet.",
        "",
    ]
    for item in pairs:
        reviewer_index.extend(
            [
                f"## {item['deep_pair_id']}",
                "",
                f"- Source paper: {item['title']}",
                f"- Variant A PDF: `{Path(item['reviewer_visible_files'][0]).name}`",
                f"- Variant B PDF: `{Path(item['reviewer_visible_files'][1]).name}`",
                "",
            ]
        )
    write_text(PACKET_DIR / "deep_pdf_reviewer_index.md", "\n".join(reviewer_index))

    checklist = """# School/NUS Expert Review Ethics And Launch Checklist

This checklist is coordinator-facing. It is designed for a minimal-risk blind
expert evaluation of regenerated ML/AI mini-paper artifacts.

## Before Recruitment

- Identify whether the work is intended for publication or public research
  dissemination. If yes, treat it as human-participant research until the
  institution says otherwise.
- Ask the relevant school, department, supervisor, DERC, IRB, or ethics office
  whether the study requires review or an exemption determination.
- Prepare the reviewer information sheet, consent/privacy note, recruitment
  email, instructions, score sheet, and anonymized A/B artifacts.
- Do not self-declare exemption in the paper or repository.
- Do not recruit students over whom the author has grading, employment, or
  supervisory power.
- If compensation or gift cards are used, record the policy and amount before
  recruitment.

## During Collection

- Use anonymized reviewer IDs such as R1, R2, and R3.
- Keep the condition keys hidden until all planned ratings are collected or the
  preregistered stopping rule is reached.
- Store completed CSVs separately from the reviewer-visible packet.
- Collect only the fields needed for the study: scores, winner, rationale, and
  optional expertise category.

## After Collection

- Validate each CSV with `scripts/summarize_human_expert_blind_reviews.py`.
- Report aggregate scores only.
- If a reviewer asks to withdraw before analysis, remove their rows and record
  the exclusion without naming them.
- Do not claim independent human evidence until at least the preregistered
  minimum number of valid expert rows has been collected.
"""
    write_text(PACKET_DIR / "school_expert_ethics_launch_checklist.md", checklist)

    form_spec = """# Online Form Builder Specification

This file describes how to turn the blind review packet into a Qualtrics,
Google Forms, Microsoft Forms, or REDCap-style form. It is coordinator-facing.

## Recommended Sections

1. Information and consent screen.
2. Reviewer metadata:
   - anonymized reviewer ID,
   - expertise category: faculty, postdoc, PhD student, master's student,
     advanced undergraduate researcher, other,
   - years reading ML/AI papers: 0-1, 2-4, 5+.
3. Main six text A/B pairs.
4. Optional three deep-case PDF A/B pairs.
5. Final free-text comment.

## Per-Pair Fields

For each pair, include:

- `winner`: A, B, tie.
- `A_problem_framing`: integer 1-5.
- `A_method_specificity`: integer 1-5.
- `A_experiment_design`: integer 1-5.
- `A_limitation_honesty`: integer 1-5.
- `A_claim_calibration`: integer 1-5.
- `A_overall_quality`: integer 1-5.
- The same six fields for B.
- `rationale`: short free text.

## Blinding Requirements

- Do not include `condition_key.json` or `deep_pdf_condition_key.json` in the
  form.
- Use only pair IDs and neutral Variant A/B labels.
- Randomize pair order if the form system allows it, but keep A/B labels fixed
  within each pair so the hidden key remains valid.
"""
    write_text(PACKET_DIR / "online_form_builder_spec.md", form_spec)

    tracking_path = PACKET_DIR / "expert_reviewer_tracking_template.csv"
    with tracking_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "reviewer_id",
                "expertise_category",
                "affiliation_group",
                "invited_date",
                "consent_received",
                "completed_date",
                "valid_rows",
                "notes",
            ]
        )
        for rid in ["R1", "R2", "R3", "R4", "R5"]:
            writer.writerow([rid, "", "", "", "", "", "", ""])

    summary = json.loads((PACKET_DIR / "summary.json").read_text(encoding="utf-8"))
    reviewer_visible = set(summary.get("reviewer_visible_files", []))
    reviewer_visible.update(
        [
            _rel(PACKET_DIR / "deep_pdf_reviewer_index.md"),
            *[path for item in pairs for path in item["reviewer_visible_files"]],
        ]
    )
    hidden = set(summary.get("hidden_files", []))
    hidden.update(
        [
            _rel(PACKET_DIR / "deep_pdf_condition_key.json"),
            _rel(PACKET_DIR / "school_expert_ethics_launch_checklist.md"),
            _rel(PACKET_DIR / "online_form_builder_spec.md"),
            _rel(PACKET_DIR / "expert_reviewer_tracking_template.csv"),
        ]
    )
    summary.update(
        {
            "school_expert_ready_status": "prepared_no_human_ratings_yet",
            "preferred_reviewer_pool": "NUS-affiliated or school-affiliated ML/AI faculty, postdocs, PhD students, or advanced research students",
            "crowd_evaluation_boundary": "Prolific or crowd-worker evaluation is supplementary unless ML/AI expertise is verified.",
            "ethics_boundary": "Recruitment should proceed only after institutional ethics review, departmental review, or exemption determination.",
            "deep_pdf_pair_count": len(pairs),
            "deep_pdf_reviewer_index": _rel(PACKET_DIR / "deep_pdf_reviewer_index.md"),
            "deep_pdf_condition_key": _rel(PACKET_DIR / "deep_pdf_condition_key.json"),
            "school_expert_ready_files": [
                _rel(PACKET_DIR / "school_expert_ethics_launch_checklist.md"),
                _rel(PACKET_DIR / "online_form_builder_spec.md"),
                _rel(PACKET_DIR / "expert_reviewer_tracking_template.csv"),
                _rel(PACKET_DIR / "deep_pdf_reviewer_index.md"),
            ],
            "reviewer_visible_files": sorted(reviewer_visible),
            "hidden_files": sorted(hidden),
        }
    )
    (PACKET_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ready_summary = {
        "status": "school_expert_ready_prepared_no_human_ratings_yet",
        "timestamp_utc": _utc_now(),
        "packet_dir": _rel(PACKET_DIR),
        "deep_pdf_pair_count": len(pairs),
        "reviewer_visible_deep_pdf_files": [path for item in pairs for path in item["reviewer_visible_files"]],
        "hidden_files": [
            _rel(PACKET_DIR / "deep_pdf_condition_key.json"),
            _rel(PACKET_DIR / "school_expert_ethics_launch_checklist.md"),
            _rel(PACKET_DIR / "online_form_builder_spec.md"),
            _rel(PACKET_DIR / "expert_reviewer_tracking_template.csv"),
        ],
        "claim_boundary": "This prepares recruitment and optional PDF review materials. It is not completed human expert evidence.",
    }
    (PACKET_DIR / "school_expert_ready_summary.json").write_text(
        json.dumps(ready_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps({"summary": _rel(PACKET_DIR / "school_expert_ready_summary.json"), "deep_pdf_pairs": len(pairs)}, indent=2))


if __name__ == "__main__":
    main()
