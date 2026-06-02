# Review Frontier Signal Probe

- Run ID: `review_frontier_signal_probe_20260602_214500`
- Status: `review_frontier_signal_probe`
- Citation frontier source: `docs/co_pilot_ai_scientist_v3/experiments/retrospective_frontier_citation_probe_20260602_213000/summary.json`

## Aggregate

- Papers evaluated: `6`
- Papers with frontier terms: `5`
- Review snippets scored: `16`
- Review beats paper-context cases: `0`
- Review beats generated artifact cases: `0`
- Latent delayed-value candidate cases: `0`
- Mean best-review score: `0.1431`
- Mean paper-context score: `0.2369`
- Mean review-guided-artifact score: `0.1906`
- Best-review gate counts: `{"evaluator_stress_test": 1, "scientific_taste_prior": 2, "structured_feedback": 2}`

## Per Paper

- `openreview_sample_1`: frontier quality `thin_relevance_filtered_citation_graph`; paper context `0.1`; review-guided artifact `0.05`; best review `0.0469` via `evaluator_stress_test`; pattern `paper_or_artifact_already_contains_signal`
- `openreview_sample_2`: frontier quality `possible_match_drift_rejected`; paper context `0.1`; review-guided artifact `0.05`; best review `0.0` via `structured_feedback`; pattern `not_scored_no_frontier_terms`
- `openreview_sample_17`: frontier quality `usable_relevance_filtered_citation_graph`; paper context `0.3312`; review-guided artifact `0.3375`; best review `0.2906` via `scientific_taste_prior`; pattern `paper_or_artifact_already_contains_signal`
- `openreview_sample_34`: frontier quality `usable_relevance_filtered_citation_graph`; paper context `0.1875`; review-guided artifact `0.2344`; best review `0.0938` via `structured_feedback`; pattern `paper_or_artifact_already_contains_signal`
- `openreview_sample_49`: frontier quality `usable_relevance_filtered_citation_graph`; paper context `0.3281`; review-guided artifact `0.1875`; best review `0.1406` via `scientific_taste_prior`; pattern `paper_or_artifact_already_contains_signal`
- `openreview_sample_64`: frontier quality `thin_relevance_filtered_citation_graph`; paper context `0.2375`; review-guided artifact `0.1437`; best review `0.1437` via `structured_feedback`; pattern `paper_or_artifact_already_contains_signal`

## Claim Boundary

This probe screens historical review snippets for lexical overlap with later citation-derived frontier terms. It identifies candidate taste/insight signals that may deserve human-in-the-loop routing, but it does not prove causality, review quality, or long-term SOTA alignment. The current sample is six papers and should be treated as design evidence for retrospective mining.
