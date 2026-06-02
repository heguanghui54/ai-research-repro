# Temporal Frontier Replay Audit

Audit date: `2026-06-02T10:10:56Z`

Status: `pass_with_negative_delayed_value_evidence`

## Summary

- Spec: `docs/co_pilot_ai_scientist_v3/temporal_frontier_replay_spec.json`
- Protocol: `docs/co_pilot_ai_scientist_v3/retrospective_frontier_alignment_protocol.json`
- Required replay conditions present: `True`
- Delayed-value definition complete: `True`

## Archived Probe Results

- Citation-backed papers: `6`
- Relevance-filtered later citations: `80`
- Citation delayed-value cases: `0`
- Citation short-term-positive/long-term-negative cases: `3`
- Review snippets scored: `16`
- Review snippets beating paper context: `0`
- Semantic successful judgements: `5`
- Semantic winner counts: `{'paper_context': 4, 'review_guided_artifact': 1}`
- Semantic delayed-value candidates: `0`

## Candidate Mining

- Reviews screened: `473`
- Papers screened: `160`
- Delayed-value replay candidates: `120`
- Candidate rate: `0.2537`
- Long-horizon positive candidates: `84`
- Short-term repair signals: `90`

## Claim Boundary

TFR is operationalized and auditable, but the archived probes are negative for delayed-value human-review evidence. Candidate mining can prioritize which historical comments should enter expensive replay, but these candidates are not positive delayed-value cases until paper-only, review-guided, and shuffled controls are judged against later frontier evidence.

## Warnings

- No delayed-value review signal is found in the current archived TFR probes.
