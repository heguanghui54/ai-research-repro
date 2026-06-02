# Citation-Backed Retrospective Frontier Probe

- Run ID: `retrospective_frontier_citation_probe_20260602_213000`
- Status: `citation_backed_retrospective_frontier_probe`
- Citation source: `Semantic Scholar Graph API with OpenAlex fallback`

## Aggregate

- Papers with retrieved citations: `5` / `6`
- Citations after relevance filtering: `80`
- Thin citation-graph papers: `2`
- Possible match-drift papers: `1`
- Frontier quality counts: `{"possible_match_drift_rejected": 1, "thin_relevance_filtered_citation_graph": 2, "usable_relevance_filtered_citation_graph": 3}`
- Winner counts: `{"not_scored_no_frontier_terms": 1, "paper_only": 3, "review_guided": 1, "shuffled_review_control": 1}`
- Mean scores: `{"paper_only": 0.23, "review_guided": 0.21, "shuffled_review_control": 0.248}`
- Review-guided minus paper-only delta: `-0.02`
- Review-guided minus shuffled-control delta: `-0.038`
- Delayed-value cases: `0`
- Short-term-positive/long-term-negative cases: `3`

## Per Paper

- `openreview_sample_1`: `Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback`; winner `shuffled_review_control`; citations used `1`; scores `{"paper_only": 0.04, "review_guided": 0.0, "shuffled_review_control": 0.23}`; temporal pattern `short_term_positive_long_term_negative`; frontier quality `thin_relevance_filtered_citation_graph`
- `openreview_sample_2`: `Forked Diffusion for Conditional Graph Generation`; winner `not_scored_no_frontier_terms`; citations used `0`; scores `{"paper_only": 0.0, "review_guided": 0.0, "shuffled_review_control": 0.0}`; temporal pattern `mixed_or_tie`; frontier quality `possible_match_drift_rejected`
- `openreview_sample_17`: `Knowledge Unlearning for Mitigating Privacy Risks in Language Models`; winner `paper_only`; citations used `38`; scores `{"paper_only": 0.39, "review_guided": 0.32, "shuffled_review_control": 0.29}`; temporal pattern `short_term_positive_long_term_negative`; frontier quality `usable_relevance_filtered_citation_graph`
- `openreview_sample_34`: `​​What learning algorithm is in-context learning? Investigations with linear models`; winner `review_guided`; citations used `33`; scores `{"paper_only": 0.1, "review_guided": 0.25, "shuffled_review_control": 0.2}`; temporal pattern `short_and_long_term_positive`; frontier quality `usable_relevance_filtered_citation_graph`
- `openreview_sample_49`: `Unifying semi-supervised and robust learning by mixup`; winner `paper_only`; citations used `6`; scores `{"paper_only": 0.34, "review_guided": 0.25, "shuffled_review_control": 0.29}`; temporal pattern `short_term_positive_long_term_negative`; frontier quality `usable_relevance_filtered_citation_graph`
- `openreview_sample_64`: `CausalAF: Causal Autoregressive Flow for Safety-Critical Scenes Generation`; winner `paper_only`; citations used `2`; scores `{"paper_only": 0.28, "review_guided": 0.23, "shuffled_review_control": 0.23}`; temporal pattern `mixed_or_tie`; frontier quality `thin_relevance_filtered_citation_graph`

## Claim Boundary

This is a lightweight citation-backed pilot using retrieved Semantic Scholar metadata and simple term-overlap scoring. It is stronger than manual descriptors but still not a full citation graph reconstruction, blinded expert review, or proof of long-term SOTA alignment. It filters citations by lexical relevance, but thin or topically broad citation graphs can still produce misleading frontier terms.
