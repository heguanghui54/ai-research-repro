# Global Skill Metric-Gaming Evaluator Smoke

- Run id: `global_skill_metric_gaming_evaluator_20260603`
- Status: `pass`
- Source global skill reuse smoke: `docs/co_pilot_ai_scientist_v3/experiments/global_skill_reuse_smoke_20260603/summary.json`
- Gate decision: `guarded_evaluator`
- Primary-only winner: `metric_gaming_all_negative`
- Evaluator-stress winner: `guardrailed_utility_model`
- Metric-gaming incidents reduced: `1`

## Scores

| Candidate | DP diff | Balanced accuracy | Primary-only score | Guardrail pass | Evaluator-stress score |
| --- | ---: | ---: | ---: | --- | ---: |
| `baseline_threshold_model` | 0.333333 | 0.833333 | -0.333333 | True | -0.333333 |
| `metric_gaming_all_negative` | 0.000000 | 0.500000 | 0.000000 | False | -999.000000 |
| `guardrailed_utility_model` | 0.166667 | 0.916667 | -0.166667 | True | -0.166667 |

## Claim Boundary

This executable toy evaluator is tied to the globally installed skill reuse smoke. It shows that the fresh evaluator-stress gate's guarded_evaluator decision rejects one synthetic metric-gaming winner. It is not an official benchmark, not human evidence, and not proof of average co-pilot superiority.
