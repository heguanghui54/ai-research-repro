# Semantic Frontier Judge Probe

- Run ID: `semantic_frontier_judge_probe_20260602_223000`
- Status: `semantic_frontier_judge_probe`
- Judge model: `gpt-4o-mini`

## Aggregate

- Successful judgements: `5` / `5`
- Winner counts: `{"paper_context": 4, "review_guided_artifact": 1}`
- Latent delayed-value candidates: `0`
- Semantic frontier-steering candidates: `0`
- Mean scores: `{"best_review_snippet": {"actionable_research_control": 3.2, "novelty_taste_signal": 2.8, "semantic_frontier_alignment": 3}, "paper_context": {"actionable_research_control": 4, "novelty_taste_signal": 3.8, "semantic_frontier_alignment": 4.2}, "review_guided_artifact": {"actionable_research_control": 4, "novelty_taste_signal": 3.4, "semantic_frontier_alignment": 3.4}}`

## Per Paper

- `openreview_sample_1`: winner `paper_context`; pattern `paper_context_remains_stronger`; reason: paper_context provides a comprehensive overview that directly aligns with future research directions.
- `openreview_sample_17`: winner `review_guided_artifact`; pattern `short_and_semantic_positive`; reason: It explicitly outlines a method for unlearning specific sequences which could significantly steer future research directions.
- `openreview_sample_34`: winner `paper_context`; pattern `paper_context_remains_stronger`; reason: The paper context provides strong alignment with later research while detailing actionable insights for future experiments.
- `openreview_sample_49`: winner `paper_context`; pattern `paper_context_remains_stronger`; reason: The paper_context has the highest alignment with the later citing papers and proposes actionable research strategies.
- `openreview_sample_64`: winner `paper_context`; pattern `paper_context_remains_stronger`; reason: The paper_context has the highest semantic alignment with later citing papers and presents clear actionable insights.

## Claim Boundary

This is a small model-judged semantic probe over citation-derived frontier metadata. It addresses the lexical-overlap limitation but remains model-routed and non-causal; it should be treated as a prioritization signal for future human expert review, not as proof of delayed-value scientific taste.
