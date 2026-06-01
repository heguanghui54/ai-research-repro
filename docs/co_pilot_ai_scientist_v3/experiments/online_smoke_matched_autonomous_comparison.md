# Online Smoke Matched Autonomous Comparison

This comparison adds a same-FML-step autonomous baseline for the first online full-gate smoke trajectory. Lower MAE is better.

| Path | FML steps | Best validation MAE | Test MAE | Notes |
| --- | ---: | ---: | ---: | --- |
| Human-gated online smoke continuation | 3 | 1.149610 | 0.862015 | Two-draft frontier, branch gate selects step 2, then one selected-snapshot continuation step. |
| Autonomous AI Scientist-v2 baseline | 3 | 0.354147 | 0.428516 | Same task/model with 3 steps and no human branch gate. |

The autonomous baseline outperformed the human-gated continuation on held-out test MAE by 0.433500. This is a negative result for performance improvement, while the online full-gate smoke remains useful as orchestration evidence.

The selected branch before continuation had test MAE 0.646224; the one-step continuation worsened it to 0.862015. This reinforces the need for evaluator and claim gates before reporting any human-gating advantage.

## Artifacts

- Human-gated trajectory: `online_full_gate_smoke_20260601_145720/trajectory.json`
- Human-gated branch frontier: `online_full_gate_smoke_20260601_145720/branch_frontier_summary.json`
- Human-gated continuation: `online_full_gate_smoke_20260601_145720/selected_continuation_summary.json`
- Autonomous baseline: `online_smoke_autonomous_matched_3step/summary.json`
