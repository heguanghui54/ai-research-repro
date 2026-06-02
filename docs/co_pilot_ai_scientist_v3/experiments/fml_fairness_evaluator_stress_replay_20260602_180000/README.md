# FML Fairness Evaluator-Stress Replay

- Run ID: `fml_fairness_evaluator_stress_replay_20260602_180000`
- Status: `pass`
- Benchmark: `FML-Bench Fairness_fairlearn`
- Linked live skill invocation: `docs/co_pilot_ai_scientist_v3/experiments/live_skill_invocation_smoke_20260602_170000/summary.json`
- Primary-only winner: `metric_gaming_all_negative`
- Evaluator-stress decision: `abort_no_valid_non_degenerate_improvement`
- Metric-gaming incidents reduced: `1`

## Scores

| Variant | Test DPD abs | Test balanced accuracy | Primary-only score | Utility pass | Improves baseline | Accepted for continuation |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `baseline_reference` | 0.173030 | 0.763862 | -0.173030 | True | False | False |
| `api_repaired_candidate` | 0.317603 | 0.818491 | -0.317603 | True | False | False |
| `metric_gaming_all_negative` | 0.000000 | 0.500000 | -0.000000 | False | True | False |

## Interpretation

On archived FML-Bench Fairness_fairlearn outputs, the primary fairness metric alone selects the degenerate all-negative predictor because it achieves zero demographic parity difference. The evaluator-stress gate rejects that branch with a balanced-accuracy utility floor and also refuses to continue the API-repaired candidate because it worsens the baseline fairness metric. The correct gate action is therefore to abort the Fairness continuation until a non-degenerate candidate improves both fairness and utility constraints.

## Claim Boundary

This is a replay over archived real FML-Bench Fairness_fairlearn evaluation artifacts. It supports evaluator-gate design against metric gaming, but it does not show a Fairness improvement, does not rerun the remote benchmark, and does not prove that IGRE improves average benchmark performance.
