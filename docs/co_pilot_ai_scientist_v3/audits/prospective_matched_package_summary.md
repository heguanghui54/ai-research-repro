# Prospective Matched-Budget Package Summary

This table summarizes what the currently passing prospective packages show.
It complements the package audit: passing the audit means the evidence shape
is present; this summary records whether the measured outcome is positive,
negative, or only a format/feasibility signal.

## Aggregate

- Packages summarized: 6
- Co-pilot wins: 3
- Autonomous or tied wins: 3
- Complete attention gates: 6/6
- Complete taste/insight gates: 6/6
- Total recorded active review minutes: 17.00

## Packages

| Package | Benchmark | Metric | Direction | Co-pilot | Autonomous | Delta | Winner | Claim implication |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `prospective_matched_fml_causality_20260602_000001` | FML-bench | mae_mean | lower | 0.646224 | 0.624703 | 0.021520 | autonomous_or_tie | Negative co-pilot performance result for this small FML budget; supports prospective package feasibility, not superiority. |
| `prospective_matched_fml_causality_20260602_010002` | FML-bench | mae_mean | lower | 0.646224 | 0.296399 | 0.349825 | autonomous_or_tie | Negative co-pilot performance result for this small FML budget; supports prospective package feasibility, not superiority. |
| `prospective_matched_fml_fairness-fairlearn_20260602_002821` | FML-bench | abs_demographic_parity_diff_mean | lower | n/a | 0.172152 | n/a | autonomous_or_tie | Negative co-pilot performance result for this small FML budget; supports prospective package feasibility, not superiority. |
| `prospective_matched_micro_pilot_20260602_000001` | controlled_micro_task | mean_normalized_score | higher | 0.984419 | 0.596214 | 0.388205 | co_pilot | Positive controlled micro-task result; supports evidence-shape and mechanistic feasibility, not paper-quality or general superiority. |
| `prospective_matched_micro_pilot_20260603_ssh_maxcut` | controlled_micro_task | mean_normalized_score | higher | 0.984419 | 0.596214 | 0.388205 | co_pilot | Positive controlled micro-task result; supports evidence-shape and mechanistic feasibility, not paper-quality or general superiority. |
| `prospective_matched_open_data_multitask_20260603` | open_data_sklearn_builtin | test_balanced_accuracy | higher | 0.934008 | 0.919064 | 0.014944 | co_pilot | Positive but narrow open-data evaluator-stress result: the gate changes selection only on the imbalanced stress task and improves mean balanced accuracy slightly. This supports selective gate triggering, not broad superiority. |

## Interpretation

The current prospective evidence is deliberately mixed. The controlled
Max-Cut micro-pilot is positive for a human-selected branch, but it is not
an AI Scientist-v2 task and should not be used as a paper-quality result.
The FML-bench Causality packages are stronger as benchmark-shaped packages,
but they are negative for co-pilot performance at the current two-step budget.
The open-data multi-task pilot adds a middle rung: across five sklearn
tasks, the evaluator-stress gate changes selection only on the synthetic
imbalanced stress task, giving a small positive mean balanced-accuracy
delta while preserving ties on the four clean built-in tasks.
Together, these packages support the IGRE logging and matched-budget
protocol, while preserving the central limitation: human taste and insight
are high-variance search interventions whose value must be tested across
more tasks, seeds, budgets, and paper-quality outcomes.
