# Internal Review: openreview_sample_1

- Title: Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback
- Winner: `six_gate_hybrid`
- Overall delta six_gate_minus_raw: `1.6`

## Scores

| Condition | Method | Experiment | Claim | Frontier | Actionability | Overall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_review_guided | 2 | 2 | 3 | 1 | 2 | 2 |
| six_gate_hybrid | 4 | 3 | 4 | 3 | 4 | 3.6 |

## Rationale

The six-gate artifact is favored when it converts raw review text into explicit frontier steering, evaluator stress, structured feedback, and claim-calibration actions. The raw-review artifact remains competitive when it contains concrete method or experiment details without adding gate overhead.

## Claim Boundary

Deterministic internal rubric review only; not human expert evidence, not independent model review, and not a benchmark-executed rerun.
