# Delayed-Value Replay Case Audit

- Audit date: `2026-06-02T15:27:16Z`
- Status: `pass`
- Run dir: `docs/co_pilot_ai_scientist_v3/experiments/delayed_value_replay_case_paper_105_review_1_20260602_235500`
- Case ID: `paper_105_review_1`
- Live model calls: `2`
- Model delayed-value label: `positive`
- Strict delayed-value label: `mixed_or_inconclusive`
- Winner short-term: `tie`
- Winner frontier: `tie`

## Strict Rule Checks

- raw_review_guided: short_ok=False, frontier_ok=True, control_ok=True, action_ok=True, specific_ok=True
- six_gate_hybrid_guided: short_ok=False, frontier_ok=True, control_ok=True, action_ok=True, specific_ok=True

## Errors

- None

## Warnings

- raw model judge labeled the case positive, but strict preregistered rule does not

## Claim Boundary

A pass means one live four-condition replay case was generated and scored, with the delayed-value label checked against the preregistered rule. It does not mean benchmark experiments or human expert ratings were run.
