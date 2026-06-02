# Gate-Outcome Attribution Probe

- Run ID: `gate_outcome_attribution_probe_20260602_191500`
- Status: `pass`
- Source equal-context ablation: `docs/co_pilot_ai_scientist_v3/experiments/openreview_equal_context_ablation_20260602_142000/summary.json`
- Papers: `6`
- Review models: `gpt-4o-mini, claude-3-7-sonnet-latest`

## Policy Scores

| Policy | Aligned outcome score | Positive contribution | Negative contribution | Nonzero contributions |
| --- | ---: | ---: | ---: | ---: |
| `no_gate` | 0.000000 | 0.000000 | 0.000000 | 0 |
| `full_igre` | 75.166660 | 75.166660 | 0.000000 | 12 |
| `single_scientific_taste_prior` | 12.333333 | 12.333333 | 0.000000 | 2 |
| `single_evaluator_stress_test` | 37.249994 | 37.249994 | 0.000000 | 6 |
| `single_frontier_steering` | 0.000000 | 0.000000 | 0.000000 | 0 |
| `single_structured_feedback` | 25.583333 | 25.583333 | 0.000000 | 4 |
| `single_claim_calibration` | 0.000000 | 0.000000 | 0.000000 | 0 |
| `random_gate_mean_512_seeds` | 15.264972 | n/a | n/a | n/a |

## Gate Attribution

| Gate | Papers with signal | Total gate utility | Mean aligned delta when present |
| --- | ---: | ---: | ---: |
| `scientific_taste_prior` | 2 | 24.666666 | 0.500000 |
| `evaluator_stress_test` | 6 | 71.666666 | 0.472222 |
| `frontier_steering` | 0 | 0.000000 | 0.000000 |
| `structured_feedback` | 4 | 59.666666 | 0.375000 |
| `claim_calibration` | 0 | 0.000000 | 0.000000 |

## Interpretation

The full IGRE policy obtains aligned-outcome score `75.166660`. The best
single-gate policy is `single_evaluator_stress_test` with score
`37.249994`. The random single-gate baseline
averages `15.264972` over
`512` seeds.

This suggests that the same review text that routes into multiple gates also
aligns with observed downstream score improvements in the equal-context
regeneration probe. It is a downstream attribution analysis, not a causal
ablation with newly generated single-gate artifacts.

## Claim Boundary

This is a post-hoc attribution over six OpenReview regeneration pairs and model-review scores. It supports downstream gate-quality analysis as a design signal, but it does not prove causal improvement, independent human validity, or benchmark superiority.
