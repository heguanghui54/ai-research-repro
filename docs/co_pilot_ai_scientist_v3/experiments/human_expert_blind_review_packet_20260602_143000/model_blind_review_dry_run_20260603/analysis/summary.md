# Model-Only Blind Packet Dry-Run Summary

- Status: `model_only_dry_run_not_human_evidence`
- Score CSV: `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/model_blind_review_dry_run_20260603/model_score_sheet.csv`
- Condition key: `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/condition_key.json`
- Target condition: `review_guided`
- Comparator condition: `context_control_unrelated_reviews`
- Valid rows: `8`
- Independent raters: `2`
- Positive evidence threshold met: `False`

## Win Counts

- `review_guided`: `0`
- `context_control_unrelated_reviews`: `7`
- `tie`: `1`
- `other_condition`: `0`

## Mean Delta

- Mean target-comparator delta: `-1.145833` (95% bootstrap CI `-1.666667`, `-0.708333`; n=8)
- Exact binomial p excluding ties: `0.015625`
- Fleiss kappa over condition winners: `None`

## Invalid Rows

- None

## Claim Boundary

Human blind-review evidence is positive only if enough valid expert rows are collected under the preregistered protocol. Empty template or underpowered summaries are evaluation-readiness artifacts only.

## Model-Only Boundary

This dry run is not independent human expert evidence.
