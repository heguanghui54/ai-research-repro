# Delayed-Value Replay Case Execution

- Run ID: `delayed_value_replay_case_paper_37_review_1_20260603_004000`
- Timestamp UTC: `2026-06-02T15:59:09Z`
- Case ID: `paper_37_review_1`
- Title: `Learning Weighted Representations for Generalization Across Designs`
- Generation model: `gpt-4o-mini`
- Judge model: `gpt-4o-mini`
- Live model calls: `2`
- Winner short-term: `tie`
- Winner frontier: `six_gate_hybrid_guided`
- Delayed-value label: `mixed_or_inconclusive`

## Scores

| Condition | Short-term | Frontier | Actionability | Specificity | Claim calibration | Overall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `paper_only` | 4.0 | 3.0 | 4.0 | 4.0 | 4.0 | 4.0 |
| `raw_review_guided` | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 | 4.0 |
| `six_gate_hybrid_guided` | 3.0 | 5.0 | 3.0 | 3.0 | 4.0 | 4.0 |
| `shuffled_review_control` | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 |

## Delayed-Value Rationale

The artifacts demonstrate strong potential for advancing causal inference methods, particularly in handling design shifts.

## Condition Rationales

- `paper_only`: The plan is clear and actionable, with a strong hypothesis and method. However, it lacks some frontier alignment.
- `raw_review_guided`: This artifact aligns well with frontier themes and provides actionable insights, making it a strong candidate.
- `six_gate_hybrid_guided`: While it has excellent frontier alignment, the actionability and specificity could be improved.
- `shuffled_review_control`: This artifact is less aligned with frontier themes and lacks clarity in its actionability.

## Claim Boundary

This is one live model-generated four-condition mini-paper replay. It scores research-plan artifacts only; it does not rerun the original paper benchmarks, collect human expert ratings, or prove delayed-value review efficacy.
