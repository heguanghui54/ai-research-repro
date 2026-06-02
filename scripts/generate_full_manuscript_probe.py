#!/usr/bin/env python3
"""Generate matched full-manuscript probes from one prospective package.

The output is a reproducible manuscript-generation probe, not a new
end-to-end discovery run. It asks a narrow question: given the same archived
FML matched-budget evidence, can the IGRE/co-pilot package and the autonomous
baseline each be rendered into a complete, claim-calibrated paper-shaped
manuscript?
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = (
    ROOT
    / "docs/co_pilot_ai_scientist_v3/experiments/"
    / "prospective_matched_fml_causality_20260602_000001"
)


SECTIONS = [
    "Abstract",
    "1. Introduction",
    "2. Related Work",
    "3. Method",
    "4. Experimental Setup",
    "5. Results",
    "6. Claim Audit",
    "7. Limitations",
    "8. Conclusion",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _metric(summary: dict[str, Any], key: str) -> float | None:
    if key == "test":
        value = summary.get("test_result", {}).get("primary_metric")
    else:
        value = summary.get("best_val_metric")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def _delta(autonomous: float | None, co_pilot: float | None) -> float | None:
    if autonomous is None or co_pilot is None:
        return None
    return autonomous - co_pilot


def _gate_text(gate: dict[str, Any]) -> str:
    attention = gate.get("attention_cost", {})
    taste = gate.get("taste_insight", {})
    options = gate.get("options", [])
    options_text = "; ".join(
        f"{option.get('option_id')} validation score {option.get('score'):.6f}"
        for option in options
        if isinstance(option.get("score"), (int, float))
    )
    return (
        f"The frontier gate reviewed {len(options)} candidate branches "
        f"({options_text}) and selected `{gate.get('human_decision')}`. "
        f"The recorded active review time is "
        f"{attention.get('active_review_minutes', 'n/a')} minutes, and the "
        f"taste/insight score is {taste.get('taste_insight_score', 'n/a')}. "
        f"The qualitative rationale is: {taste.get('qualitative_rationale', 'n/a')}"
    )


def _co_pilot_manuscript(
    manifest: dict[str, Any],
    co_pilot: dict[str, Any],
    autonomous: dict[str, Any],
    trajectory: dict[str, Any],
    gate: dict[str, Any],
) -> str:
    co_val = _metric(co_pilot, "val")
    co_test = _metric(co_pilot, "test")
    auto_val = _metric(autonomous, "val")
    auto_test = _metric(autonomous, "test")
    test_delta = _delta(auto_test, co_test)
    return f"""# Insight-Gated Research Evolution on a Matched FML-Bench Pilot

## Abstract

This generated manuscript probe renders the prospective package
`{manifest['package_id']}` as a full paper-shaped IGRE/co-pilot manuscript.
The system inserts a human frontier-steering gate into an AI Scientist-v2-style
FML-bench run, records attention cost and scientific taste/insight, and compares
the selected branch with a matched autonomous baseline. The result is mixed:
the co-pilot branch obtains validation MAE {_fmt(co_val)} and test MAE
{_fmt(co_test)}, while the autonomous baseline obtains validation MAE
{_fmt(auto_val)} and test MAE {_fmt(auto_test)}. Lower MAE is better, so the
test delta autonomous-minus-co-pilot is {_fmt(test_delta)}. The contribution is
therefore evidence of a reproducible human-gated research trajectory format,
not evidence that human gates improve average performance.

## 1. Introduction

Automated AI research systems can run idea generation, code editing, benchmark
execution, and draft writing with limited human involvement. IGRE asks a
different question: where should a human scientist intervene when the valuable
signal is not fully captured by a scalar metric? In this package, the human
gate is not treated as a guaranteed improvement. It is treated as a
high-variance search intervention that may sometimes hurt average short-budget
metrics but can preserve scientific taste, unusual problem selection, and
claim responsibility.

The manuscript is generated from archived artifacts rather than a fresh online
trajectory. That distinction matters: it can test whether the package contains
enough evidence to write a complete, calibrated manuscript, but it cannot prove
that the whole system autonomously produced a top-conference paper.

## 2. Related Work

The run is inspired by AI Scientist-v2-style benchmark execution and paper
writing, AI Co-Scientist-style hypothesis organization, and AlphaEvolve-style
program evolution. The method here is not a direct copy of those systems. IGRE
renames and adapts the process around four paper-specific requirements:
frontier steering, taste/insight logging, evaluator stress testing, and claim
calibration. Because official AlphaEvolve core code is unavailable, the broader
package uses OpenEvolve only as an AlphaEvolve-style substrate for reproducible
program-search subproblems.

## 3. Method

IGRE represents the research process as a gated trajectory. Automated agents
produce candidate branches, evaluators score them, and selected human gates may
intervene when scalar metrics are too narrow. Each gate records candidate
options, the chosen branch, a rationale, attention cost, and scientific
taste/insight fields. The goal is not to convert taste into a hidden reward
model. The goal is to make normally tacit scientific judgment auditable enough
to compare against autonomous baselines.

For this FML package, the key gate is:

> {_gate_text(gate)}

## 4. Experimental Setup

Both variants use `{co_pilot.get('benchmark')}`, model
`{co_pilot.get('model')}`, provider `{co_pilot.get('provider')}`, and the same
two-step budget. The co-pilot path first samples two frontier branches and
continues the selected one. The autonomous baseline receives the same task,
model family, tool access, and step budget but no human gate. The metric is
MAE on the Causality benchmark; lower is better.

## 5. Results

| Variant | Validation MAE | Test MAE |
| --- | ---: | ---: |
| IGRE/co-pilot selected branch | {_fmt(co_val)} | {_fmt(co_test)} |
| Matched autonomous baseline | {_fmt(auto_val)} | {_fmt(auto_test)} |

The autonomous baseline is better on this held-out test metric. This negative
result is useful: it prevents the manuscript from claiming that a human gate is
automatically beneficial under tight budgets. The positive result is narrower:
the package demonstrates that a prospective, matched-budget, human-gated
AI Scientist-v2-style evidence bundle can be produced and audited.

## 6. Claim Audit

Supported: the package contains a prospective co-pilot trajectory, matched
autonomous baseline, complete human gate record, final claim audit, and
manuscript artifact.

Unsupported: this run does not show that human gates improve average benchmark
performance, human attention efficiency, or full paper quality. It also does
not establish top-conference empirical support.

## 7. Limitations

The run covers one FML task, one model family, one short budget, and one
human-gate decision. The branch choice had tied validation scores, so the
scientific-taste intervention mainly tests logging and trajectory shaping, not
metric superiority. Independent expert review and multi-task, multi-seed
matched comparisons remain necessary.

## 8. Conclusion

This probe supports IGRE as a distinctive, reproducible co-pilot pattern for
making human scientific taste and attention cost visible inside AI research
loops. It should be presented as pilot evidence and manuscript-readiness
evidence, not as proof that co-pilot systems outperform autonomous AI
Scientist-v2.
"""


def _autonomous_manuscript(
    manifest: dict[str, Any],
    co_pilot: dict[str, Any],
    autonomous: dict[str, Any],
) -> str:
    co_val = _metric(co_pilot, "val")
    co_test = _metric(co_pilot, "test")
    auto_val = _metric(autonomous, "val")
    auto_test = _metric(autonomous, "test")
    test_delta = _delta(auto_test, co_test)
    return f"""# Autonomous AI Scientist-v2 Baseline on a Matched FML-Bench Pilot

## Abstract

This generated manuscript probe renders the matched autonomous baseline from
`{manifest['package_id']}` as a full paper-shaped manuscript. The baseline uses
the same FML-bench task, model family, tool access, and two-step budget as the
co-pilot package, but it omits human frontier steering. It obtains validation
MAE {_fmt(auto_val)} and test MAE {_fmt(auto_test)}, outperforming the co-pilot
package's test MAE {_fmt(co_test)} under this short-budget setting. The result
supports the autonomous baseline as a necessary negative control, not as a
general proof that autonomous research agents are superior.

## 1. Introduction

A strong human-in-the-loop claim needs a matched autonomous comparator. Without
that comparator, any generated paper can confuse better logging with better
science. This manuscript therefore centers the autonomous path. It asks whether
the same AI Scientist-v2-style execution budget can produce a competitive FML
result without human gate intervention.

## 2. Related Work

The baseline follows the automated research loop used by AI Scientist-v2-style
systems: generate candidate code changes, execute benchmark feedback, keep the
best candidate, and summarize the result. It does not attempt to model human
scientific taste, and it does not include AlphaEvolve/OpenEvolve-style
subproblem escalation.

## 3. Method

The autonomous run receives benchmark instructions and a fixed two-step budget.
It proposes and evaluates candidate changes using `{autonomous.get('model')}`
through `{autonomous.get('provider')}`. No human gate selects among branches,
and no attention-cost or taste/insight record is generated. This makes the
baseline less expressive as a scientific collaboration system but cleaner as a
metric-only control.

## 4. Experimental Setup

The task is `{autonomous.get('benchmark')}` with metric direction `lower`.
Target files include `{', '.join(autonomous.get('task_config', {}).get('target_files', []))}`.
The baseline primary metric before the short run is
{_fmt(autonomous.get('baseline_primary_metric'))}. The matched co-pilot package
uses the same task, model family, tool access, and step budget.

## 5. Results

| Variant | Validation MAE | Test MAE |
| --- | ---: | ---: |
| Autonomous matched baseline | {_fmt(auto_val)} | {_fmt(auto_test)} |
| IGRE/co-pilot comparator | {_fmt(co_val)} | {_fmt(co_test)} |

Lower is better. The autonomous-minus-co-pilot test delta is
{_fmt(test_delta)}, so the autonomous run wins on this test metric. This result
is a warning against assuming that human intervention is always positive.

## 6. Claim Audit

Supported: the autonomous baseline is a matched negative control for the FML
prospective package and beats the co-pilot variant on the recorded test MAE.

Unsupported: the baseline does not measure paper quality, novelty, scientific
taste, long-horizon research value, or the chance of rare high-impact
discoveries.

## 7. Limitations

The baseline covers one task and one short budget. It is optimized for the
available scalar metric, so it may miss scientific questions that require
field taste, mechanistic framing, or unusual benchmark choice. A serious
comparison must include multiple tasks, seeds, budgets, and independent paper
quality review.

## 8. Conclusion

The autonomous baseline is strong enough to keep IGRE claims honest. It shows
that under a tight FML budget, removing the human gate can improve the scalar
metric. Future claims for human participation should therefore target upper-tail
scientific value and claim calibration, not average short-run metric gains.
"""


def _score_manuscript(text: str, *, has_gate: bool, wins_metric: bool) -> dict[str, Any]:
    headings = [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]
    section_hits = sum(1 for section in SECTIONS if section in headings)
    limitation_terms = sum(
        text.lower().count(term)
        for term in ["unsupported", "limitation", "not evidence", "not prove", "not as proof"]
    )
    metric_terms = sum(text.count(term) for term in ["MAE", "delta", "lower is better"])
    score = {
        "section_completeness": round(section_hits / len(SECTIONS) * 5, 2),
        "evidence_grounding": min(5.0, round(2.0 + metric_terms * 0.35, 2)),
        "claim_calibration": min(5.0, round(3.0 + limitation_terms * 0.18, 2)),
        "method_distinctness": 4.2 if has_gate else 3.2,
        "metric_result_strength": 4.0 if wins_metric else 2.8,
    }
    score["overall"] = round(
        (
            score["section_completeness"]
            + score["evidence_grounding"]
            + score["claim_calibration"]
            + score["method_distinctness"]
            + score["metric_result_strength"]
        )
        / 5,
        2,
    )
    return score


def _write_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# Matched Full-Manuscript Generation Probe",
        "",
        "This probe generates two full paper-shaped manuscripts from the same",
        "prospective FML matched-budget package. It is archived-evidence manuscript",
        "generation, not a fresh end-to-end research trajectory.",
        "",
        "## Artifacts",
        "",
        f"- Co-pilot full manuscript: `{summary['co_pilot_full_manuscript']}`",
        f"- Autonomous full manuscript: `{summary['autonomous_full_manuscript']}`",
        f"- JSON audit: `{summary['json']}`",
        "",
        "## Deterministic Rubric",
        "",
        "| Variant | Overall | Completeness | Evidence | Calibration | Method distinctness | Metric strength |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, label in [
        ("co_pilot", "IGRE/co-pilot"),
        ("autonomous", "Autonomous baseline"),
    ]:
        score = summary["scores"][key]
        lines.append(
            f"| {label} | {score['overall']:.2f} | "
            f"{score['section_completeness']:.2f} | {score['evidence_grounding']:.2f} | "
            f"{score['claim_calibration']:.2f} | {score['method_distinctness']:.2f} | "
            f"{score['metric_result_strength']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            summary["interpretation"],
            "",
            "## Limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in summary["limitations"])
    lines.append("")
    return "\n".join(lines)


def _update_repro_manifest(paths: list[str], summary: dict[str, Any]) -> None:
    manifest_path = ROOT / "docs/co_pilot_ai_scientist_v3/repro_manifest.json"
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        if path not in artifacts:
            artifacts.append(path)
    manifest["status"] = "pilot_package_with_full_manuscript_probe"
    manifest["matched_full_manuscript_generation_probe"] = {
        "status": "archived_evidence_probe_not_fresh_end_to_end",
        "script": "scripts/generate_full_manuscript_probe.py",
        "summary": summary["markdown"],
        "json": summary["json"],
        "package_id": summary["package_id"],
        "co_pilot_overall": summary["scores"]["co_pilot"]["overall"],
        "autonomous_overall": summary["scores"]["autonomous"]["overall"],
        "interpretation": "full_structure_and_claim_calibration_probe_only",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _update_package_manifest(package_dir: Path, summary: dict[str, Any]) -> None:
    manifest_path = package_dir / "prospective_manifest.json"
    manifest = _load_json(manifest_path)
    manifest["full_manuscript_generation_probe"] = {
        "summary": summary["markdown"],
        "json": summary["json"],
        "co_pilot_full_manuscript": summary["co_pilot_full_manuscript"],
        "autonomous_full_manuscript": summary["autonomous_full_manuscript"],
        "co_pilot_overall": summary["scores"]["co_pilot"]["overall"],
        "autonomous_overall": summary["scores"]["autonomous"]["overall"],
        "metric_winner": summary["metric_result"]["winner"],
        "limitation": "archived_evidence_probe_not_fresh_end_to_end",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", default=str(DEFAULT_PACKAGE))
    parser.add_argument("--update-manifest", action="store_true")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    if not package_dir.is_absolute():
        package_dir = ROOT / package_dir

    manifest = _load_json(package_dir / "prospective_manifest.json")
    co_pilot = _load_json(ROOT / manifest["co_pilot_branch_summary"])
    autonomous = _load_json(ROOT / manifest["autonomous_baseline"])
    trajectory = _load_json(ROOT / manifest["co_pilot_trajectory"])
    gate_path = ROOT / manifest["human_gate_logs"][0]
    gate = _load_json(gate_path)

    output_dir = package_dir / "full_manuscript_probe"
    output_dir.mkdir(parents=True, exist_ok=True)

    co_text = _co_pilot_manuscript(manifest, co_pilot, autonomous, trajectory, gate)
    auto_text = _autonomous_manuscript(manifest, co_pilot, autonomous)
    co_path = output_dir / "co_pilot_full_manuscript.md"
    auto_path = output_dir / "autonomous_full_manuscript.md"
    co_path.write_text(co_text, encoding="utf-8")
    auto_path.write_text(auto_text, encoding="utf-8")

    co_test = _metric(co_pilot, "test")
    auto_test = _metric(autonomous, "test")
    co_wins_metric = co_test is not None and auto_test is not None and co_test < auto_test
    auto_wins_metric = co_test is not None and auto_test is not None and auto_test < co_test
    summary: dict[str, Any] = {
        "package_id": manifest["package_id"],
        "status": "matched_full_manuscript_generation_probe",
        "fresh_end_to_end_trajectory": False,
        "co_pilot_full_manuscript": _rel(co_path),
        "autonomous_full_manuscript": _rel(auto_path),
        "scores": {
            "co_pilot": _score_manuscript(co_text, has_gate=True, wins_metric=co_wins_metric),
            "autonomous": _score_manuscript(auto_text, has_gate=False, wins_metric=auto_wins_metric),
        },
        "metric_result": {
            "co_pilot_test_mae": co_test,
            "autonomous_test_mae": auto_test,
            "lower_is_better": True,
            "winner": "co_pilot" if co_wins_metric else "autonomous" if auto_wins_metric else "tie_or_unknown",
        },
        "interpretation": (
            "The co-pilot manuscript has stronger method distinctness and explicit "
            "taste/attention logging, while the autonomous manuscript has the "
            "stronger scalar FML result. This supports a manuscript-generation "
            "and claim-calibration capability, not a top-conference superiority claim."
        ),
        "limitations": [
            "Generated from archived evidence rather than a fresh online end-to-end trajectory.",
            "Deterministic rubric is an internal audit aid, not independent peer review.",
            "Single FML task, one model family, one short budget, and one human gate.",
            "Does not prove that human gates improve paper quality or benchmark performance.",
        ],
    }
    json_path = output_dir / "summary.json"
    md_path = output_dir / "summary.md"
    summary["json"] = _rel(json_path)
    summary["markdown"] = _rel(md_path)
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_write_summary(summary), encoding="utf-8")

    paths = [_rel(co_path), _rel(auto_path), _rel(json_path), _rel(md_path), "scripts/generate_full_manuscript_probe.py"]
    if args.update_manifest:
        _update_package_manifest(package_dir, summary)
        _update_repro_manifest(paths, summary)

    print(json.dumps({"summary": _rel(md_path), "json": _rel(json_path)}, indent=2))


if __name__ == "__main__":
    main()
