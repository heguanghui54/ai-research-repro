# Citation-Backed Retrospective Frontier Probe

- Run ID: `retrospective_frontier_citation_probe_20260602_163000`
- Status: `citation_backed_retrospective_frontier_probe`
- Citation source: `Semantic Scholar Graph API with OpenAlex fallback`

## Aggregate

- Papers with retrieved citations: `1` / `3`
- Citations after relevance filtering: `13`
- Thin citation-graph papers: `0`
- Possible match-drift papers: `1`
- Frontier quality counts: `{"no_relevant_citations": 1, "possible_match_drift_rejected": 1, "usable_relevance_filtered_citation_graph": 1}`
- Winner counts: `{"not_scored_no_frontier_terms": 2, "review_guided": 1}`
- Mean scores: `{"paper_only": 0.3067, "review_guided": 0.32, "shuffled_review_control": 0.24}`
- Review-guided minus paper-only delta: `0.0133`
- Review-guided minus shuffled-control delta: `0.08`
- Delayed-value cases: `0`
- Short-term-positive/long-term-negative cases: `0`

## Per Paper

- `openreview_sample_1`: `Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback`; winner `not_scored_no_frontier_terms`; citations used `0`; scores `{"paper_only": 0.0, "review_guided": 0.0, "shuffled_review_control": 0.0}`; temporal pattern `mixed_or_tie`; frontier quality `no_relevant_citations`
- `openreview_sample_2`: `Forked Diffusion for Conditional Graph Generation`; winner `not_scored_no_frontier_terms`; citations used `0`; scores `{"paper_only": 0.0, "review_guided": 0.0, "shuffled_review_control": 0.0}`; temporal pattern `mixed_or_tie`; frontier quality `possible_match_drift_rejected`
- `openreview_sample_17`: `Knowledge Unlearning for Mitigating Privacy Risks in Language Models`; winner `review_guided`; citations used `13`; scores `{"paper_only": 0.3067, "review_guided": 0.32, "shuffled_review_control": 0.24}`; temporal pattern `short_and_long_term_positive`; frontier quality `usable_relevance_filtered_citation_graph`

## Claim Boundary

This is a lightweight citation-backed pilot using retrieved Semantic Scholar metadata and simple term-overlap scoring. It is stronger than manual descriptors but still not a full citation graph reconstruction, blinded expert review, or proof of long-term SOTA alignment. It filters citations by lexical relevance, but thin or topically broad citation graphs can still produce misleading frontier terms.
