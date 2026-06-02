# Live TFR Replay Aggregate Summary

- Run ID: `live_tfr_replay_aggregate_20260603_003500`
- Timestamp UTC: `2026-06-02T16:00:34Z`
- Executed case count: `3`
- Same-model raw positive labels: `3`
- Strict positive labels: `0`
- Cross-model successful judges: `3`
- Cross-model strict positive labels: `0`

## Same-Model Case Results

| Case | Model label | Strict label | Short-term winner | Frontier winner |
| --- | --- | --- | --- | --- |
| `paper_105_review_1` | `positive` | `mixed_or_inconclusive` | `tie` | `tie` |
| `paper_132_review_2` | `positive` | `mixed_or_inconclusive` | `tie` | `six_gate_hybrid_guided` |
| `paper_37_review_1` | `positive` | `mixed_or_inconclusive` | `tie` | `six_gate_hybrid_guided` |

## Cross-Model Results

- Source `docs/co_pilot_ai_scientist_v3/experiments/delayed_value_replay_case_paper_105_review_1_20260602_235500`
  - `claude-3-7-sonnet-latest`: strict `mixed_or_inconclusive`, model `mixed_or_inconclusive`, frontier winner `six_gate_hybrid_guided`
  - archived errors: `{'gemini-2.5-flash': 'JSONDecodeError("Expecting \',\' delimiter: line 11 column 6 (char 623)")'}`
- Source `docs/co_pilot_ai_scientist_v3/experiments/delayed_value_replay_case_paper_132_review_2_20260603_002500`
  - `claude-3-7-sonnet-latest`: strict `mixed_or_inconclusive`, model `mixed_or_inconclusive`, frontier winner `six_gate_hybrid_guided`
- Source `docs/co_pilot_ai_scientist_v3/experiments/delayed_value_replay_case_paper_37_review_1_20260603_004000`
  - `claude-3-7-sonnet-latest`: strict `mixed_or_inconclusive`, model `negative`, frontier winner `six_gate_hybrid_guided`

## Interpretation

Across three live four-condition TFR cases, the same-model GPT judge labels all three cases positive before deterministic rule repair, but the strict preregistered delayed-value rule finds zero positive cases. Claude cross-model review also finds zero strict positive cases while often selecting the six-gate artifact as the frontier winner. In the third case, Claude's model label is negative because the review signals are too generic and the generated artifacts remain poorly differentiated. This supports TFR as a model-optimism guard and failure-mode diagnostic, not as evidence that delayed-value review signals have already been found.

## Claim Boundary

This aggregate summarizes model-generated mini-paper replay artifacts and model judges. It does not include benchmark reruns, human expert ratings, or proof that human reviews improve long-horizon scientific outcomes.
