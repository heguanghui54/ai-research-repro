# Delayed-Value Replay Cross-Model Judge Audit

- Audit date: `2026-06-02T15:32:26Z`
- Status: `pass`
- Run dir: `docs/co_pilot_ai_scientist_v3/experiments/delayed_value_replay_cross_model_judge_20260603_001500`
- Models attempted: `claude-3-7-sonnet-latest, gemini-2.5-flash`
- Models succeeded: `claude-3-7-sonnet-latest`
- Models failed: `gemini-2.5-flash`
- Strict label counts: `{'mixed_or_inconclusive': 1}`
- Frontier winner counts: `{'six_gate_hybrid_guided': 1}`

## Judgement Checks

- `claude-3-7-sonnet-latest`: strict `mixed_or_inconclusive`, model `mixed_or_inconclusive`, frontier winner `six_gate_hybrid_guided`, short-term winner `tie`

## Errors

- None

## Warnings

- models with archived errors: ['gemini-2.5-flash']

## Claim Boundary

A pass means at least one independent model judge scored the existing four-condition replay and the strict delayed-value label was archived. It is still model evaluation, not human expert review or benchmark execution.
