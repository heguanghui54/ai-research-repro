# Retrospective Frontier Alignment Smoke

- Run ID: `retrospective_frontier_alignment_smoke_20260602_160000`
- Status: `deterministic_retrospective_frontier_alignment_smoke`
- Source regeneration: `docs/co_pilot_ai_scientist_v3/experiments/openreview_guided_regeneration_probe_20260602_073500/summary.json`
- Control source: `docs/co_pilot_ai_scientist_v3/experiments/openreview_equal_context_ablation_20260602_142000/summary.json`

## Aggregate

- Winner counts: `{"review_guided": 1, "shuffled_review_control": 5}`
- Mean scores: `{"paper_only": 0.3428, "review_guided": 0.3378, "shuffled_review_control": 0.4233}`
- Review-guided minus paper-only mean delta: `-0.005`
- Review-guided minus shuffled-control mean delta: `-0.0855`
- Delayed-value cases: `0`
- Short-term-positive/long-term-negative cases: `3`

## Per Paper

- `openreview_sample_1`: winner `review_guided`, scores `{"paper_only": 0.2367, "review_guided": 0.24, "shuffled_review_control": 0.2367}`, temporal pattern `short_and_long_term_positive`
- `openreview_sample_2`: winner `shuffled_review_control`, scores `{"paper_only": 0.2033, "review_guided": 0.24, "shuffled_review_control": 0.4133}`, temporal pattern `short_and_long_term_positive`
- `openreview_sample_17`: winner `shuffled_review_control`, scores `{"paper_only": 0.3433, "review_guided": 0.3067, "shuffled_review_control": 0.3767}`, temporal pattern `short_term_positive_long_term_negative`
- `openreview_sample_34`: winner `shuffled_review_control`, scores `{"paper_only": 0.52, "review_guided": 0.45, "shuffled_review_control": 0.5533}`, temporal pattern `short_term_positive_long_term_negative`
- `openreview_sample_49`: winner `shuffled_review_control`, scores `{"paper_only": 0.41, "review_guided": 0.3433, "shuffled_review_control": 0.4433}`, temporal pattern `short_term_positive_long_term_negative`
- `openreview_sample_64`: winner `shuffled_review_control`, scores `{"paper_only": 0.3433, "review_guided": 0.4467, "shuffled_review_control": 0.5167}`, temporal pattern `mixed_or_tie`

## Claim Boundary

This is a deterministic smoke test for the retrospective frontier-alignment protocol. Frontier descriptors are manually specified placeholders, not a citation-backed SOTA reconstruction. Use it as pipeline evidence, not as proof that historical reviewers predicted later research.
