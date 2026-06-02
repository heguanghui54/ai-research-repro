# Delayed-Value Replay Cross-Model Judge

- Run ID: `delayed_value_replay_cross_model_judge_20260603_001500`
- Timestamp UTC: `2026-06-02T15:30:52Z`
- Source case run: `docs/co_pilot_ai_scientist_v3/experiments/delayed_value_replay_case_paper_105_review_1_20260602_235500`
- Models attempted: `claude-3-7-sonnet-latest, gemini-2.5-flash`
- Models succeeded: `claude-3-7-sonnet-latest`
- Strict label counts: `{'mixed_or_inconclusive': 1}`
- Model label counts: `{'mixed_or_inconclusive': 1}`
- Frontier winner counts: `{'six_gate_hybrid_guided': 1}`
- Any model/strict disagreement: `False`

## Per-Model Results

- `claude-3-7-sonnet-latest`: model label `mixed_or_inconclusive`, strict label `mixed_or_inconclusive`, short-term winner `tie`, frontier winner `six_gate_hybrid_guided`

## Errors

- `gemini-2.5-flash`: JSONDecodeError("Expecting ',' delimiter: line 11 column 6 (char 623)")

## Claim Boundary

This cross-model judge scores already generated four-condition mini-paper artifacts. It reduces same-model scoring bias but is still model evaluation, not human expert review or benchmark execution.
