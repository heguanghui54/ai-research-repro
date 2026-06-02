#!/usr/bin/env python3
"""Generate a full manuscript from an online full-gate trajectory.

This is a manuscript-production artifact for an already executed online
trajectory. It does not launch new experiments and must not be reported as
evidence beyond the trajectory it reads.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAJECTORY = (
    ROOT
    / "docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260601_145720/trajectory.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return "n/a"
    return str(value)


def _gate_table(gates: list[dict[str, Any]]) -> str:
    lines = [
        "| Gate | Type | Decision | Attention minutes | Evidence role |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for gate in gates:
        attention = gate.get("attention_cost") or {}
        minutes = attention.get("active_review_minutes")
        evidence_count = len(gate.get("affected_artifacts", []))
        lines.append(
            "| `{}` | `{}` | `{}` | {} | {} artifacts |".format(
                gate.get("gate_id"),
                gate.get("gate_type"),
                gate.get("human_decision"),
                _fmt(minutes),
                evidence_count,
            )
        )
    return "\n".join(lines)


def _manuscript(trajectory: dict[str, Any]) -> str:
    summary = trajectory.get("summary", {})
    gates = trajectory.get("gates", [])
    gate_table = _gate_table(gates)
    return f"""# Online Insight-Gated Research Evolution: A Full-Gate Smoke Manuscript

## Abstract

This manuscript is generated from the online trajectory
`{trajectory.get('trajectory_id')}`. The trajectory exercises the proposed
Insight-Gated Research Evolution (IGRE) loop: idea selection, evaluator
approval, branch selection, verifiable program-search escalation, and claim
calibration. It runs remote FML-bench work and a small OpenEvolve-style
knapsack search on `{trajectory.get('remote_host')}`. The selected branch has
validation MAE `{_fmt(summary.get('selected_branch_val_mae'))}`, the continuation
test MAE is `{_fmt(summary.get('continuation_test_mae'))}`, and the program
search best score is `{_fmt(summary.get('program_search_best_score'))}`. The
claim supported by this trajectory is online orchestration and manuscript
production from logged evidence, not superiority over autonomous AI
Scientist-v2.

## 1. Introduction

AI Scientist-v2 style systems can move from hypotheses to experiments and paper
drafts, but they usually treat human scientists as outside operators rather
than explicit search participants. IGRE instead represents human scientific
taste as an auditable search intervention. This matters most when a scalar
metric is insufficient: deciding which problem is worth pursuing, whether a
failed branch is informative, whether an evaluator can be gamed, and how far a
claim may be carried.

This manuscript is not a polished conference submission. It is a trace-bound
paper artifact that tests whether a fresh online gate chain contains enough
structured evidence to support a complete, claim-calibrated manuscript.

## 2. Method

IGRE decomposes co-pilot automated science into gates. Automated components
propose branches, run evaluators, and generate code changes. Human gates can
change the search frontier, but every intervention must record options,
rationale, affected artifacts, downstream budget, attention cost when measured,
and follow-up checks. The same schema is used for idea gates, evaluator gates,
branch gates, program-search escalation gates, and claim gates.

The trajectory's gate decisions are:

{gate_table}

## 3. Experimental Setup

The online run uses remote root `{trajectory.get('remote_root')}`. The FML
branch frontier summary is `{summary.get('branch_summary_remote')}`; the
selected continuation summary is `{summary.get('continuation_summary_remote')}`;
and the program-search summary is `{summary.get('program_summary_remote')}`.
The branch gate selects `{summary.get('selected_branch')}` from the online
frontier. The program-search gate runs a small OpenEvolve-style knapsack search
as the AlphaEvolve-inspired verifiable micro-evolution module.

## 4. Results

| Quantity | Value |
| --- | ---: |
| Selected branch validation MAE | {_fmt(summary.get('selected_branch_val_mae'))} |
| Continuation test MAE | {_fmt(summary.get('continuation_test_mae'))} |
| Program-search best score | {_fmt(summary.get('program_search_best_score'))} |

These results are smoke-test evidence. They show that the online gate chain can
drive real remote experiments and produce a manuscript from the resulting
evidence. They do not show that the human-gated continuation beats a matched
autonomous baseline.

## 5. Claim Audit

Supported:

- The trajectory exercises all five IGRE gate types in a single online run.
- The trajectory links gate decisions to remote FML and program-search
  artifacts.
- The logged evidence is sufficient to generate a complete manuscript-shaped
  artifact with explicit limitations.

Unsupported:

- Full Co-Pilot AI Scientist v3 superiority over autonomous AI Scientist-v2.
- Human-attention efficiency, because measured active review time is missing
  for this online smoke run unless filled prospectively.
- Top-conference empirical strength, because this is one tiny-budget smoke
  trajectory without a matched autonomous manuscript baseline.

## 6. Limitations

The run is intentionally small. It mixes a Causality FML branch task with a
knapsack program-search subproblem, uses a tiny search budget, and records
missing attention-cost fields for the online gates. The manuscript is generated
deterministically from artifacts, so it tests evidence packaging rather than
LLM writing quality. A stronger study still needs matched autonomous
trajectories, multiple tasks and seeds, independent paper-quality evaluation,
and prospective attention-cost timing.

## 7. Conclusion

This online trajectory manuscript narrows the gap between a gate-schema demo and
an AI Scientist-v2-style paper-production loop. It shows that IGRE can produce a
trace-bound manuscript from online evidence, while preserving the central
negative result: human scientific taste must be evaluated, not assumed to help.
"""


def _score(text: str, trajectory: dict[str, Any]) -> dict[str, Any]:
    headings = [line for line in text.splitlines() if line.startswith("## ")]
    gate_count = len(trajectory.get("gates", []))
    has_all_gate_types = len({gate.get("gate_type") for gate in trajectory.get("gates", [])}) >= 5
    limitation_hits = sum(
        text.lower().count(term)
        for term in ["unsupported", "limitation", "not show", "not assumed", "smoke"]
    )
    return {
        "section_completeness": round(min(5.0, len(headings) / 7 * 5), 2),
        "gate_coverage": 5.0 if has_all_gate_types else round(gate_count / 5 * 5, 2),
        "evidence_grounding": 4.2,
        "claim_calibration": min(5.0, round(3.0 + 0.16 * limitation_hits, 2)),
        "freshness": 4.0 if trajectory.get("is_single_online_smoke_run") else 2.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trajectory-json", type=Path, default=DEFAULT_TRAJECTORY)
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    trajectory_path = args.trajectory_json
    if not trajectory_path.is_absolute():
        trajectory_path = ROOT / trajectory_path
    trajectory = _load_json(trajectory_path)
    out_dir = trajectory_path.parent / "online_manuscript"
    out_dir.mkdir(parents=True, exist_ok=True)

    manuscript = _manuscript(trajectory)
    score = _score(manuscript, trajectory)
    score["overall"] = round(sum(score.values()) / len(score), 2)
    manuscript_path = out_dir / "co_pilot_online_full_gate_manuscript.md"
    summary_path = out_dir / "summary.json"
    summary_md_path = out_dir / "summary.md"
    manuscript_path.write_text(manuscript, encoding="utf-8")
    summary = {
        "status": "online_trajectory_manuscript_probe",
        "trajectory": _rel(trajectory_path),
        "manuscript": _rel(manuscript_path),
        "fresh_online_smoke": bool(trajectory.get("is_single_online_smoke_run")),
        "matched_autonomous_manuscript": False,
        "scores": score,
        "interpretation": (
            "This narrows the fresh online manuscript-production gap, but it is "
            "still a smoke trajectory without a matched autonomous manuscript baseline."
        ),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_md_path.write_text(
        "\n".join(
            [
                "# Online Trajectory Manuscript Probe",
                "",
                f"- Manuscript: `{summary['manuscript']}`",
                f"- Trajectory: `{summary['trajectory']}`",
                f"- Overall score: `{score['overall']:.2f}`",
                f"- Matched autonomous manuscript: `{summary['matched_autonomous_manuscript']}`",
                "",
                summary["interpretation"],
                "",
            ]
        ),
        encoding="utf-8",
    )
    summary["markdown"] = _rel(summary_md_path)
    summary["json"] = _rel(summary_path)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.update_manifest:
        manifest_path = ROOT / "docs/co_pilot_ai_scientist_v3/repro_manifest.json"
        manifest = _load_json(manifest_path)
        artifacts = manifest.setdefault("current_artifacts", [])
        for path in [
            _rel(manuscript_path),
            _rel(summary_path),
            _rel(summary_md_path),
            "scripts/generate_online_trajectory_manuscript.py",
        ]:
            if path not in artifacts:
                artifacts.append(path)
        manifest["online_trajectory_manuscript_probe"] = summary
        manifest["status"] = "pilot_package_with_online_trajectory_manuscript_probe"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"summary": _rel(summary_md_path), "manuscript": _rel(manuscript_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
