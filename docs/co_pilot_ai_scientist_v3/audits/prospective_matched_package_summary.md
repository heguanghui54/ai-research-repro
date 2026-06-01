# Prospective Matched-Budget Package Summary

This table summarizes what the currently passing prospective packages show.
It complements the package audit: passing the audit means the evidence shape
is present; this summary records whether the measured outcome is positive,
negative, or only a format/feasibility signal.

## Aggregate

- Packages summarized: 2
- Co-pilot wins: 1
- Autonomous or tied wins: 1
- Complete attention gates: 2/2
- Complete taste/insight gates: 2/2
- Total recorded active review minutes: 5.00

## Packages

| Package | Benchmark | Metric | Direction | Co-pilot | Autonomous | Delta | Winner | Claim implication |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `prospective_matched_fml_causality_20260602_000001` | FML-bench | mae_mean | lower | 0.646224 | 0.624703 | 0.021520 | autonomous_or_tie | Negative co-pilot performance result for this small FML budget; supports prospective package feasibility, not superiority. |
| `prospective_matched_micro_pilot_20260602_000001` | controlled_micro_task | mean_normalized_score | higher | 0.984419 | 0.596214 | 0.388205 | co_pilot | Positive controlled micro-task result; supports evidence-shape and mechanistic feasibility, not paper-quality or general superiority. |

## Interpretation

The current prospective evidence is deliberately mixed. The controlled
Max-Cut micro-pilot is positive for a human-selected branch, but it is not
an AI Scientist-v2 task and should not be used as a paper-quality result.
The FML-bench Causality package is stronger as a benchmark-shaped package,
but it is negative for co-pilot performance at the current two-step budget.
Together, these packages support the IGRE logging and matched-budget
protocol, while preserving the central limitation: human taste and insight
are high-variance search interventions whose value must be tested across
more tasks, seeds, budgets, and paper-quality outcomes.
