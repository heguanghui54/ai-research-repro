# Single-Gate Artifact Ablation

- Run ID: `single_gate_artifact_ablation_20260602_203000`
- Status: `pass`
- Generation model: `gpt-4o-mini`
- Reviewer models: `gpt-4o-mini, claude-3-7-sonnet-latest`
- Papers: `6`
- Live model calls: `3`

## Mean Overall By Condition

| Condition | Mean overall |
| --- | ---: |
| `baseline` | 2.9166 |
| `full_review_guided` | 3.5000 |
| `single_evaluator_stress_test` | 3.6667 |
| `single_scientific_taste_prior` | 3.5000 |
| `single_structured_feedback` | 3.6250 |

## Aggregate

- Winner counts: `{"baseline": 3, "full_review_guided": 2, "single_evaluator_stress_test": 6, "single_structured_feedback": 1}`
- Best single gate counts: `{"single_evaluator_stress_test": 9, "single_structured_feedback": 3}`
- Best single condition by mean: `single_evaluator_stress_test`
- Full review-guided minus baseline: `0.5834`
- Full review-guided minus best single: `-0.1667`
- Best single minus baseline: `0.7501`

## Interpretation

This single-gate artifact ablation generates new artifacts using only one gate-specific review signal. It therefore moves beyond post-hoc attribution. The result should be read as a small OpenReview proxy for which gates are useful in isolation and whether full review guidance still adds value over isolated gates.

## Claim Boundary

This is a six-paper, model-reviewed OpenReview proxy using generated mini-paper artifacts. It is closer to a causal gate ablation than post-hoc attribution, but it does not replace independent human expert ratings, real benchmark reruns, or multi-task AI Scientist-v2 matched experiments.
