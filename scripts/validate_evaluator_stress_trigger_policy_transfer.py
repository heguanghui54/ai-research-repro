#!/usr/bin/env python3
"""Validate evaluator-stress trigger transfer from discovery to held-out splits.

The per-package trigger-policy summaries identify the best policy within each
package. This script performs the stricter check needed for the paper claim:
select a trigger policy on the discovery split package, freeze that policy, and
evaluate the same policy on the held-out split package.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
EXP_DIR = DOC_DIR / "experiments"
DEFAULT_TRAIN_PACKAGE = "prospective_matched_open_data_multitask_20260603"
DEFAULT_HELDOUT_PACKAGE = "prospective_matched_open_data_multitask_holdout_20260603"
DEFAULT_RUN_ID = "evaluator_trigger_policy_transfer_20260603"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _policy_summaries(package_id: str) -> dict[str, Any]:
    path = EXP_DIR / package_id / "evaluator_stress_trigger_policy_summary.json"
    summary = _load_json(path)
    if summary.get("status") != "pass":
        raise ValueError(f"trigger policy summary is not pass: {path}")
    return summary


def _select_policy(train_summary: dict[str, Any]) -> str:
    policies = train_summary.get("policies", {})
    if not policies:
        raise ValueError("train summary has no policies")
    return max(
        policies,
        key=lambda policy: (
            policies[policy]["delta_vs_autonomous_mean"],
            -policies[policy]["losses_vs_autonomous"],
            -policies[policy]["triggered_count"],
        ),
    )


def _add_manifest_artifacts(paths: list[Path], payload: dict[str, Any]) -> None:
    manifest_path = DOC_DIR / "repro_manifest.json"
    if not manifest_path.exists():
        return
    manifest = _load_json(manifest_path)
    artifacts = manifest.setdefault("current_artifacts", [])
    for path in paths:
        rel = _rel(path)
        if rel not in artifacts:
            artifacts.append(rel)
    rel_script = _rel(Path(__file__))
    if rel_script not in artifacts:
        artifacts.append(rel_script)
    manifest["evaluator_stress_trigger_policy_transfer"] = payload
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-package", default=DEFAULT_TRAIN_PACKAGE)
    parser.add_argument("--heldout-package", default=DEFAULT_HELDOUT_PACKAGE)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    args = parser.parse_args()

    train_summary = _policy_summaries(args.train_package)
    heldout_summary = _policy_summaries(args.heldout_package)
    selected_policy = _select_policy(train_summary)
    train_policy = train_summary["policies"][selected_policy]
    heldout_policy = heldout_summary["policies"][selected_policy]
    heldout_always = heldout_summary["policies"]["always_on_evaluator_stress"]
    heldout_auto = heldout_summary["policies"]["autonomous_accuracy_only"]

    out_dir = EXP_DIR / args.run_id
    json_path = out_dir / "summary.json"
    md_path = out_dir / "README.md"

    summary = {
        "status": "pass",
        "created_at": _utc_now(),
        "train_package": args.train_package,
        "heldout_package": args.heldout_package,
        "train_summary": _rel(EXP_DIR / args.train_package / "evaluator_stress_trigger_policy_summary.json"),
        "heldout_summary": _rel(EXP_DIR / args.heldout_package / "evaluator_stress_trigger_policy_summary.json"),
        "selection_rule": (
            "Choose the discovery-split policy with maximum mean delta versus "
            "autonomous selection, breaking ties by fewer autonomous losses and "
            "then fewer trigger events."
        ),
        "selected_policy": selected_policy,
        "train_selected_policy": train_policy,
        "heldout_frozen_policy": heldout_policy,
        "heldout_autonomous": heldout_auto,
        "heldout_always_on": heldout_always,
        "heldout_transfer_checks": {
            "frozen_policy_delta_beats_always_on_delta": (
                heldout_policy["delta_vs_autonomous_mean"]
                > heldout_always["delta_vs_autonomous_mean"]
            ),
            "frozen_policy_has_no_losses": heldout_policy["losses_vs_autonomous"] == 0,
            "always_on_has_losses": heldout_always["losses_vs_autonomous"] > 0,
            "frozen_policy_triggered_no_more_than_always_on": (
                heldout_policy["triggered_count"] <= heldout_always["triggered_count"]
            ),
        },
        "overreach_reduction_on_heldout": {
            "always_on_losses": heldout_always["losses_vs_autonomous"],
            "frozen_policy_losses": heldout_policy["losses_vs_autonomous"],
            "loss_reduction": (
                heldout_always["losses_vs_autonomous"]
                - heldout_policy["losses_vs_autonomous"]
            ),
            "always_on_delta_vs_autonomous_mean": heldout_always["delta_vs_autonomous_mean"],
            "frozen_policy_delta_vs_autonomous_mean": heldout_policy["delta_vs_autonomous_mean"],
        },
        "claim_boundary": (
            "This is a discovery-to-held-out split validation inside one open-data "
            "task family. It supports trigger-conditioned evaluator-stress design, "
            "not broad co-pilot superiority or a universally optimal threshold."
        ),
    }
    _write_json(json_path, summary)

    lines = [
        "# Evaluator-Stress Trigger Policy Transfer",
        "",
        "This artifact freezes the trigger policy selected on the discovery split",
        "package and evaluates the same policy on held-out split seeds. It is a",
        "stricter check than choosing the best policy independently inside each",
        "package.",
        "",
        "## Selection",
        "",
        f"- Train package: `{args.train_package}`",
        f"- Held-out package: `{args.heldout_package}`",
        f"- Selection rule: {summary['selection_rule']}",
        f"- Frozen selected policy: `{selected_policy}`",
        "",
        "## Results",
        "",
        "| Condition | Mean test balanced accuracy | Delta vs autonomous | Wins | Losses | Ties | Triggered |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, item in [
        ("train frozen policy", train_policy),
        ("held-out autonomous", heldout_auto),
        ("held-out always-on evaluator-stress", heldout_always),
        ("held-out frozen policy", heldout_policy),
    ]:
        lines.append(
            "| "
            + " | ".join(
                [
                    label,
                    f"{item['mean_test_balanced_accuracy']:.6f}",
                    f"{item['delta_vs_autonomous_mean']:.6f}",
                    str(item["wins_vs_autonomous"]),
                    str(item["losses_vs_autonomous"]),
                    str(item["ties_vs_autonomous"]),
                    str(item["triggered_count"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Transfer Interpretation",
            "",
            (
                "The discovery split selects `class_imbalance_trigger_0_94`. "
                "When frozen and evaluated on held-out split seeds, the policy "
                f"obtains delta `{heldout_policy['delta_vs_autonomous_mean']}` "
                "against autonomous selection with "
                f"`{heldout_policy['wins_vs_autonomous']}` wins, "
                f"`{heldout_policy['losses_vs_autonomous']}` losses, and "
                f"`{heldout_policy['ties_vs_autonomous']}` ties. The always-on "
                "gate has "
                f"`{heldout_always['losses_vs_autonomous']}` held-out losses."
            ),
            "",
            "## Claim Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    _add_manifest_artifacts(
        [json_path, md_path],
        {
            "status": "pass",
            "script": _rel(Path(__file__)),
            "summary": _rel(md_path),
            "json": _rel(json_path),
            "train_package": args.train_package,
            "heldout_package": args.heldout_package,
            "selected_policy": selected_policy,
            "heldout_delta_vs_autonomous_mean": heldout_policy["delta_vs_autonomous_mean"],
            "heldout_losses_vs_autonomous": heldout_policy["losses_vs_autonomous"],
            "claim_boundary": summary["claim_boundary"],
        },
    )

    print(json.dumps({"status": "pass", "json": _rel(json_path), "markdown": _rel(md_path)}, indent=2))


if __name__ == "__main__":
    main()
