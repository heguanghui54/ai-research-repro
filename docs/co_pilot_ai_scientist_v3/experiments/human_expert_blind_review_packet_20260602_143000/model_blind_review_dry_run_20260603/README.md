# Model-Only Blind Packet Dry Run

- Status: `model_only_dry_run_not_human_evidence`
- Models: `gpt-4o-mini, gemini-2.5-flash`
- Pair count: `6`
- Parsed score rows: `8`
- Score CSV: `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/model_blind_review_dry_run_20260603/model_score_sheet.csv`
- Analysis JSON: `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/model_blind_review_dry_run_20260603/analysis/summary.json`
- Analysis Markdown: `docs/co_pilot_ai_scientist_v3/experiments/human_expert_blind_review_packet_20260602_143000/model_blind_review_dry_run_20260603/analysis/summary.md`

## Boundary

This run validates the blind packet and summarization pipeline only. It is not independent human expert evidence.

## Aggregate

- Win counts: `{"review_guided": 0, "context_control_unrelated_reviews": 7, "tie": 1, "other_condition": 0}`
- Mean delta: `{"mean": -1.1458333333333333, "ci95_low": -1.6666666666666667, "ci95_high": -0.7083333333333333, "n": 8}`
- Positive evidence threshold met: `False`
