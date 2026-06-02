# Metric-Gaming Evaluator-Stress Smoke

- Run ID: `metric_gaming_evaluator_stress_smoke_20260602_171500`
- Status: `pass`
- Linked live skill invocation: `docs/co_pilot_ai_scientist_v3/experiments/live_skill_invocation_smoke_20260602_170000/summary.json`
- Primary-only winner: `metric_gaming_all_negative`
- Evaluator-stress winner: `guardrailed_utility_model`
- Metric-gaming incidents reduced: `1`

## Scores

| Candidate | Demographic parity diff | Balanced accuracy | Primary-only score | Guardrail pass | Evaluator-stress score |
| --- | ---: | ---: | ---: | --- | ---: |
| `baseline_threshold_model` | 0.333333 | 0.833333 | -0.333333 | True | -0.333333 |
| `metric_gaming_all_negative` | 0.000000 | 0.500000 | 0.000000 | False | -999.000000 |
| `guardrailed_utility_model` | 0.166667 | 0.916667 | -0.166667 | True | -0.166667 |

## Claim Boundary

This is a deterministic evaluator-stress smoke linked to the live skill invocation. It demonstrates that a multi-metric guardrail can reject one synthetic metric-gaming candidate. It is not an FML-bench result, not a human-subject study, and not evidence that IGRE improves average benchmark performance.
