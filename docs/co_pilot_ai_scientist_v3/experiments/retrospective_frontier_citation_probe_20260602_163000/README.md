# Citation-Backed Retrospective Frontier Probe

- Run ID: `retrospective_frontier_citation_probe_20260602_163000`
- Status: `citation_backed_retrospective_frontier_probe`
- Citation source: `Semantic Scholar Graph API with OpenAlex fallback`

## Aggregate

- Papers with retrieved citations: `1` / `1`
- Thin citation-graph papers: `1`
- Winner counts: `{"shuffled_review_control": 1}`
- Mean scores: `{"paper_only": 0.04, "review_guided": 0.0, "shuffled_review_control": 0.08}`
- Review-guided minus paper-only delta: `-0.04`
- Review-guided minus shuffled-control delta: `-0.08`
- Delayed-value cases: `0`
- Short-term-positive/long-term-negative cases: `1`

## Per Paper

- `openreview_sample_1`: `Rejection Improves Reliability: Training LLMs to Refuse Unknown Questions Using RL from Knowledge Feedback`; winner `shuffled_review_control`; citations used `2`; scores `{"paper_only": 0.04, "review_guided": 0.0, "shuffled_review_control": 0.08}`; temporal pattern `short_term_positive_long_term_negative`

## Claim Boundary

This is a lightweight citation-backed pilot using retrieved Semantic Scholar metadata and simple term-overlap scoring. It is stronger than manual descriptors but still not a full citation graph reconstruction, blinded expert review, or proof of long-term SOTA alignment. Thin or topically broad citation graphs can produce misleading frontier terms and require relevance filtering.
