# Human Expert Blind Review Summary

- Status: `no_valid_rows`
- Score CSV: `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/score_sheet_template.csv`
- Condition key: `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/condition_key.json`
- Target condition: `review_guided`
- Comparator condition: `context_control_unrelated_reviews`
- Valid rows: `0`
- Independent raters: `0`
- Positive evidence threshold met: `False`

## Win Counts

- `review_guided`: `0`
- `context_control_unrelated_reviews`: `0`
- `tie`: `0`
- `other_condition`: `0`

## Mean Delta

- Mean target-comparator delta: unavailable
- Exact binomial p excluding ties: `None`
- Fleiss kappa over condition winners: `None`

## Invalid Rows

- line 2: `pair_01` -> invalid_or_missing_winner, missing_or_invalid_rubric_scores, missing_reviewer_id
- line 3: `pair_02` -> invalid_or_missing_winner, missing_or_invalid_rubric_scores, missing_reviewer_id
- line 4: `pair_03` -> invalid_or_missing_winner, missing_or_invalid_rubric_scores, missing_reviewer_id
- line 5: `pair_04` -> invalid_or_missing_winner, missing_or_invalid_rubric_scores, missing_reviewer_id
- line 6: `pair_05` -> invalid_or_missing_winner, missing_or_invalid_rubric_scores, missing_reviewer_id
- line 7: `pair_06` -> invalid_or_missing_winner, missing_or_invalid_rubric_scores, missing_reviewer_id

## Claim Boundary

Human blind-review evidence is positive only if enough valid expert rows are collected under the preregistered protocol. Empty template or underpowered summaries are evaluation-readiness artifacts only.
