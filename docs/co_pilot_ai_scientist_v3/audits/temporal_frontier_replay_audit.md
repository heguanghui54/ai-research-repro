# Temporal Frontier Replay Audit

Audit date: `2026-06-02T15:32:26Z`

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

## Candidate Frontier Validation

- Attempted reviews: `16`
- Scored reviews: `13`
- Not scored after match-drift guard: `3`
- Delayed-candidate mean review signal: `0.24`
- Control mean review signal: `0.176`
- Delayed minus control mean score: `0.064`

## Deep Case Triage

- Selected cases: `3`
- Mean selected triage score: `8.2197`
- Mean selected review-title delta: `0.1867`
- `paper_132_review_2` `long_horizon_positive_candidate` triage `9.1377`: Optimal Rates for Averaged Stochastic Gradient Descent under Neural Tangent Kernel Regime
- `paper_105_review_1` `delayed_value_replay_candidate` triage `7.946`: E2ENet: Dynamic Sparse Feature Fusion for Accurate and Efficient 3D Medical Image Segmentation
- `paper_37_review_1` `long_horizon_positive_candidate` triage `7.5753`: Learning Weighted Representations for Generalization Across Designs

## Executed Replay Case

- Case ID: `paper_105_review_1`
- Live model calls: `2`
- Model delayed-value label: `positive`
- Strict delayed-value label: `mixed_or_inconclusive`
- Winner short-term: `tie`
- Winner frontier: `tie`

## Cross-Model Replay Judge

- Models attempted: `['claude-3-7-sonnet-latest', 'gemini-2.5-flash']`
- Models succeeded: `['claude-3-7-sonnet-latest']`
- Models failed: `['gemini-2.5-flash']`
- Strict label counts: `{'mixed_or_inconclusive': 1}`
- Frontier winner counts: `{'six_gate_hybrid_guided': 1}`

## Claim Boundary

TFR is operationalized and auditable, but the archived probes are negative for delayed-value human-review evidence. Candidate mining can prioritize which historical comments should enter expensive replay, a small OpenAlex validation shows weak positive candidate-vs-control frontier alignment, and the deep-case triage queue now selects three concrete cases for future expensive replay. These the first live four-condition replay is mixed rather than positive under the strict preregistered rule. A cross-model judge confirms the mixed strict label while selecting the six-gate artifact as the frontier winner. These artifacts still do not prove delayed-value human-review efficacy without benchmark reruns or independent expert judgement.

## Warnings

- No delayed-value review signal is found in the current archived TFR probes.
