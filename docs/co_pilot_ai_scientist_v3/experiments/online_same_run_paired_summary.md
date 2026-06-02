# Online Same-Run Paired Smoke Summary

This file aggregates only online full-gate smoke trajectories that
contain a same-continuous-run autonomous AI Scientist-v2 baseline.
For Causality rows, lower MAE is better. Rows with no valid
scalar test metric are counted as unknown/no-valid rather than
as wins for either side.

## Aggregate

- Paired smoke count: `3`
- Co-pilot benchmark wins: `0`
- Autonomous benchmark wins: `1`
- Benchmark ties: `1`
- Benchmark unknown/no-valid: `1`
- No-valid-branch trajectories: `1`
- Mean co-pilot test MAE: `0.754120`
- Mean autonomous test MAE: `0.643337`
- Mean autonomous-minus-co-pilot test MAE: `-0.110782`
- Model-review probes: `3`
- Model-review co-pilot wins: `6`
- Model-review autonomous wins: `0`
- Model-review ties: `0`

## Records

| Trajectory | Task | No valid branch | Co-pilot test | Autonomous test | Delta auto-co | Winner | Co-pilot manuscript | Autonomous manuscript | Model-review wins |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `online_full_gate_smoke_20260602_010521` | `Causality_causalml` | False | 0.862015 | 0.640451 | -0.221564 | autonomous | 4.640000 | 3.480000 | 2/2 |
| `online_full_gate_smoke_20260602_012208` | `Causality_causalml` | False | 0.646224 | 0.646224 | -0.000000 | tie | 4.640000 | 3.480000 | 2/2 |
| `online_full_gate_smoke_20260602_013612` | `Fairness_fairlearn` | True | n/a | n/a | n/a | unknown | 4.640000 | 3.100000 | 2/2 |

## Interpretation

Repeated same-continuous online smokes support orchestration and manuscript-measurement readiness, but not co-pilot benchmark superiority. Current benchmark aggregate favors autonomous or tie.
The model-review wins are useful process checks, not independent
human expert peer review or top-conference evidence.
