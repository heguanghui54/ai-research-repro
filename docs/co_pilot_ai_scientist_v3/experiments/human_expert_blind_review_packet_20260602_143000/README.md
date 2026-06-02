# Human Expert Blind Review Packet

- Packet ID: `human_expert_blind_review_packet_20260602_143000`
- Timestamp UTC: `2026-06-02T06:21:01Z`
- Condition: `equal_context`
- Pair count: `6`
- Source regeneration run: `openreview_guided_regeneration_probe_20260602_073500`
- Equal-context source run: `openreview_equal_context_ablation_20260602_142000`

## Files

- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/instructions.md`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/score_sheet_template.csv`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/pairs/pair_01.md`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/pairs/pair_02.md`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/pairs/pair_03.md`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/pairs/pair_04.md`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/pairs/pair_05.md`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/pairs/pair_06.md`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/preregistration_analysis_plan.md`
- `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/preregistration_analysis_plan.json`

## Status

This packet prepares blind human expert evaluation. It does not contain
completed human ratings yet. The condition key is stored separately in
`condition_key.json` and should not be shown to reviewers.

The preregistration files define the planned endpoints, exact-binomial and
bootstrap reporting, stopping rule, and the distinction between useful
scientific taste/insight signals and low-utility reviewer comments. They are
coordinator-facing until ratings are complete because they name hidden
conditions.

## Score Summary Smoke

The packet includes an empty-template smoke summary at
`human_score_summary_smoke/summary.json` and
`human_score_summary_smoke/summary.md`. This smoke run intentionally reports
`no_valid_rows`; it is an evaluation-readiness check, not human evidence.

After collecting completed blind score sheets, copy the filled CSV into this
packet directory and run:

```bash
python3 scripts/summarize_human_expert_blind_reviews.py \
  --score-csv docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/<filled_score_sheet>.csv \
  --condition-key docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/condition_key.json \
  --output-dir docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/human_score_summary_completed
```

The resulting summary is positive evidence only if it satisfies the
preregistered minimum-rater and minimum-row thresholds and the reported win or
score-delta tests support the target condition.
