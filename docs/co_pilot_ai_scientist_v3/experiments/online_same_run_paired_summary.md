# Online Same-Run Paired Smoke Summary

This file aggregates only online full-gate smoke trajectories that
contain a same-continuous-run autonomous AI Scientist-v2 baseline.
Lower MAE is better for the FML Causality metric.

## Aggregate

- Paired smoke count: `2`
- Co-pilot benchmark wins: `0`
- Autonomous benchmark wins: `1`
- Benchmark ties: `1`
- Mean co-pilot test MAE: `0.754120`
- Mean autonomous test MAE: `0.643337`
- Mean autonomous-minus-co-pilot test MAE: `-0.110782`
- Model-review probes: `2`
- Model-review co-pilot wins: `4`
- Model-review autonomous wins: `0`
- Model-review ties: `0`

## Records

| Trajectory | Co-pilot test MAE | Autonomous test MAE | Delta auto-co | Winner | Co-pilot manuscript | Autonomous manuscript | Model-review wins |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `online_full_gate_smoke_20260602_010521` | 0.862015 | 0.640451 | -0.221564 | autonomous | 4.640000 | 3.480000 | 2/2 |
| `online_full_gate_smoke_20260602_012208` | 0.646224 | 0.646224 | -0.000000 | tie | 4.640000 | 3.480000 | 2/2 |

## Interpretation

Repeated same-continuous online smokes support orchestration and manuscript-measurement readiness, but not co-pilot benchmark superiority. Current benchmark aggregate favors autonomous or tie.
The model-review wins are useful process checks, not independent
human expert peer review or top-conference evidence.
