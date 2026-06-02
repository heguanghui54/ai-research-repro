#!/usr/bin/env python3
"""Power analysis for the high-tail human-participation hypothesis.

The current IGRE evidence is mixed for average short-budget performance. This
script operationalizes the alternative high-tail claim: human taste may increase
the probability of rare frontier-quality outcomes even when average benchmark
scores do not improve. It estimates how many matched autonomous vs. human-gated
runs are needed to detect such a tail-probability shift.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "co_pilot_ai_scientist_v3"
OUT_DIR = DOC_DIR / "experiments" / "high_tail_power_analysis_20260602_233000"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _log_comb(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def _hypergeom_pmf(k: int, *, population: int, success_states: int, draws: int) -> float:
    if k < 0 or k > success_states or k > draws:
        return 0.0
    failures = population - success_states
    if draws - k > failures:
        return 0.0
    log_p = (
        _log_comb(success_states, k)
        + _log_comb(failures, draws - k)
        - _log_comb(population, draws)
    )
    return math.exp(log_p)


def _fisher_one_sided_greater(copilot_success: int, autonomous_success: int, n_per_arm: int) -> float:
    """One-sided Fisher exact p-value for copilot tail rate > autonomous tail rate."""

    total_success = copilot_success + autonomous_success
    population = 2 * n_per_arm
    draws = n_per_arm
    max_success = min(total_success, draws)
    p_value = 0.0
    for k in range(copilot_success, max_success + 1):
        p_value += _hypergeom_pmf(k, population=population, success_states=total_success, draws=draws)
    return min(1.0, p_value)


def _binomial(rng: random.Random, n: int, p: float) -> int:
    return sum(1 for _ in range(n) if rng.random() < p)


def _estimate_power(
    *,
    autonomous_tail_rate: float,
    copilot_tail_rate: float,
    n_per_arm: int,
    alpha: float,
    simulations: int,
    rng: random.Random,
) -> dict[str, Any]:
    p_values = []
    copilot_successes = []
    autonomous_successes = []
    detected = 0
    for _ in range(simulations):
        c = _binomial(rng, n_per_arm, copilot_tail_rate)
        a = _binomial(rng, n_per_arm, autonomous_tail_rate)
        p_value = _fisher_one_sided_greater(c, a, n_per_arm)
        p_values.append(p_value)
        copilot_successes.append(c)
        autonomous_successes.append(a)
        if p_value <= alpha:
            detected += 1
    return {
        "n_per_arm": n_per_arm,
        "autonomous_tail_rate": autonomous_tail_rate,
        "copilot_tail_rate": copilot_tail_rate,
        "absolute_lift": round(copilot_tail_rate - autonomous_tail_rate, 4),
        "relative_lift": round(copilot_tail_rate / autonomous_tail_rate, 4)
        if autonomous_tail_rate
        else None,
        "alpha": alpha,
        "simulations": simulations,
        "estimated_power": round(detected / simulations, 4),
        "mean_copilot_tail_successes": round(mean(copilot_successes), 4),
        "mean_autonomous_tail_successes": round(mean(autonomous_successes), 4),
        "median_p_value": round(sorted(p_values)[len(p_values) // 2], 6),
    }


def _first_n_reaching(rows: list[dict[str, Any]], threshold: float) -> int | None:
    for row in rows:
        if row["estimated_power"] >= threshold:
            return int(row["n_per_arm"])
    return None


def _protocol_markdown(summary: dict[str, Any]) -> str:
    rows = summary["power_rows"]
    lines = [
        "# High-Tail Human-Participation Power Analysis",
        "",
        f"Run date: {summary['run_date']}",
        "",
        "## Purpose",
        "",
        "This protocol operationalizes the high-tail hypothesis in IGRE: human",
        "scientific taste may increase the probability of rare frontier-quality",
        "outputs even when average short-budget benchmark scores are mixed or",
        "negative. The hypothesis is not that every human gate improves every",
        "run. It is that a selected participation mode can increase the tail",
        "probability of outcomes that pass a strict quality/frontier threshold.",
        "",
        "## Tail Outcome Definition",
        "",
        "A run is counted as a high-tail success only if it satisfies all of the",
        "following preregistered conditions:",
        "",
        "1. A blinded reviewer or fixed external evaluator marks the artifact as",
        "   top-tier on the primary quality dimension.",
        "2. The artifact passes the claim-calibration gate: its claims are supported",
        "   by the evidence actually produced in the run.",
        "3. The artifact is not a metric-gaming result under the evaluator-stress",
        "   gate.",
        "4. For TFR studies, the artifact is also closer to later field-frontier",
        "   evidence than both paper-only and shuffled-review controls.",
        "",
        "For the current paper package, no positive delayed-value high-tail cases",
        "have been found. This analysis is therefore a planning artifact, not a",
        "positive result.",
        "",
        "## Statistical Test",
        "",
        "The planned primary test is a one-sided Fisher exact test comparing the",
        "high-tail success rate of human-gated/co-pilot runs against autonomous",
        "runs under matched budgets. Ties and invalid runs are reported separately",
        "and are not silently converted into wins.",
        "",
        "## Monte Carlo Power Table",
        "",
        "| Autonomous tail rate | Co-pilot tail rate | n per arm | Estimated power | Mean co-pilot successes | Mean autonomous successes |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {autonomous_tail_rate:.3f} | {copilot_tail_rate:.3f} | {n_per_arm} | "
            "{estimated_power:.3f} | {mean_copilot_tail_successes:.2f} | "
            "{mean_autonomous_tail_successes:.2f} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Design Implication",
            "",
            "Small six-paper OpenReview probes are useful for pipeline debugging but",
            "are underpowered for a rare breakthrough-probability claim. If the",
            "autonomous tail rate is 5% and human-gated participation raises it to",
            "10%, the estimated sample size needed for roughly 80% power is recorded",
            "in `summary.json` and is far larger than the current pilot. This is why",
            "the focused paper must present high-tail participation as a future",
            "study design unless independent large-scale data are collected.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--simulations", type=int, default=5000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20260602)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    scenarios = [
        (0.02, 0.05),
        (0.05, 0.10),
        (0.05, 0.15),
        (0.10, 0.15),
        (0.10, 0.20),
    ]
    n_values = [10, 20, 30, 50, 75, 100, 150, 200, 300, 500]
    rows: list[dict[str, Any]] = []
    by_scenario: list[dict[str, Any]] = []
    for auto_rate, copilot_rate in scenarios:
        scenario_rows = []
        for n in n_values:
            row = _estimate_power(
                autonomous_tail_rate=auto_rate,
                copilot_tail_rate=copilot_rate,
                n_per_arm=n,
                alpha=args.alpha,
                simulations=args.simulations,
                rng=rng,
            )
            rows.append(row)
            scenario_rows.append(row)
        by_scenario.append(
            {
                "autonomous_tail_rate": auto_rate,
                "copilot_tail_rate": copilot_rate,
                "absolute_lift": round(copilot_rate - auto_rate, 4),
                "first_n_per_arm_for_80_power": _first_n_reaching(scenario_rows, 0.8),
                "first_n_per_arm_for_50_power": _first_n_reaching(scenario_rows, 0.5),
            }
        )

    current_pilot = {
        "openreview_tfr_cases": 6,
        "citation_delayed_value_cases": 0,
        "semantic_delayed_value_candidates": 0,
        "interpretation": (
            "The current six-paper TFR probes are pipeline evidence and negative "
            "delayed-value evidence; they are not powered to detect rare high-tail effects."
        ),
    }
    summary = {
        "run_date": _utc_now(),
        "script": _rel(Path(__file__)),
        "seed": args.seed,
        "alpha": args.alpha,
        "simulations_per_cell": args.simulations,
        "test": "one_sided_fisher_exact_copilot_tail_rate_greater_than_autonomous",
        "tail_outcome_definition": {
            "blind_or_fixed_external_quality_threshold": "top-tier on primary quality/frontier dimension",
            "claim_calibration_required": True,
            "metric_gaming_rejected": True,
            "tfr_extra_condition": "review-guided artifact closer to later field frontier than paper-only and shuffled-review controls",
        },
        "current_pilot": current_pilot,
        "scenario_summary": by_scenario,
        "power_rows": rows,
        "claim_boundary": (
            "This artifact operationalizes the high-tail hypothesis and shows that "
            "large matched samples are required. It is not evidence that IGRE has "
            "already increased breakthrough probability."
        ),
    }
    summary_path = args.out_dir / "summary.json"
    protocol_path = args.out_dir / "protocol.md"
    readme_path = args.out_dir / "README.md"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    protocol = _protocol_markdown(summary)
    protocol_path.write_text(protocol, encoding="utf-8")
    readme_path.write_text(
        "# High-tail power analysis\n\n"
        "This directory contains a preregisterable power-analysis artifact for "
        "testing whether human-gated participation increases rare frontier-quality "
        "outputs. It complements the current negative TFR probes by making the "
        "high-tail claim statistically falsifiable.\n\n"
        f"- Summary: `{summary_path.name}`\n"
        f"- Protocol: `{protocol_path.name}`\n",
        encoding="utf-8",
    )
    print(json.dumps({"summary": _rel(summary_path), "protocol": _rel(protocol_path)}, indent=2))


if __name__ == "__main__":
    main()
