# Mixed And Negative Evidence Audit

- Audit date: `2026-06-02T17:38:09Z`
- Status: `pass`
- Cases: `7`

## Failure Mechanism Map

### `ungated_review_text_can_hurt_blind_quality`

- Evidence: `{"review_guided_wins": 0, "context_control_wins": 7, "ties": 1, "mean_delta": -1.1458333333333333, "status": "model_only_dry_run_not_human_evidence"}`
- Failure mechanism: Raw review text can add noise, overfit to reviewer phrasing, or distract the generator from the original technical frame.
- IGRE design implication: Route reviews into gate-specific actions before regeneration; compare against equal-context controls and blind scoring.

### `short_budget_fml_does_not_show_copilot_superiority`

- Evidence: `{"status": "mixed_underpowered_fml_matched_evidence", "formal_pair_count": 2, "claim_implication": "The formal FML Causality pairs are mixed and slightly favor autonomous on the two-pair mean. The prospective two-step FML packages and the online smoke comparison are also negative for co-pilot performance. These artifacts support branch-gate feasibility and evidence discipline, not superiority."}`
- Failure mechanism: Tiny-budget human-gated branch choice can spend attention on plausible but under-tested continuations while autonomous search keeps a stronger local metric path.
- IGRE design implication: Keep benchmark performance and manuscript quality separate; require matched multi-task reruns before claiming superiority.

### `prospective_packages_are_mixed`

- Evidence: `{"package_count": 5, "co_pilot_wins": 2, "autonomous_or_tie_wins": 3, "total_active_review_minutes": 13.0}`
- Failure mechanism: Human-selected branches help on some machine-gradeable micro-problems but do not yet generalize to end-to-end AI Scientist-v2 research benchmarks.
- IGRE design implication: Use human gates selectively where evaluator readiness and branch asymmetry are high; do not average controlled micro-task wins into paper-quality claims.

### `tfr_corrects_model_optimism_without_positive_dvrs`

- Evidence: `{"executed_case_count": 3, "same_model_raw_positive_count": 3, "strict_positive_count": 0, "cross_model_strict_positive_count": 0}`
- Failure mechanism: Model judges can label guided artifacts as positive even when the preregistered delayed-value condition is not satisfied.
- IGRE design implication: Use deterministic delayed-value rules and cross-model checks before treating future-frontier alignment as evidence.

### `citation_frontier_alignment_favors_original_context`

- Evidence: `{"aggregate": {"paper_count": 6, "papers_with_retrieved_citations": 5, "thin_citation_graph_papers": 2, "citation_count_after_relevance_filter": 80, "possible_match_drift_papers": 1, "frontier_quality_counts": {"thin_relevance_filtered_citation_graph": 2, "possible_match_drift_rejected": 1, "usable_relevance_filtered_citation_graph": 3}, "winner_counts": {"shuffled_review_control": 1, "not_scored_no_frontier_terms": 1, "paper_only": 3, "review_guided": 1}, "mean_scores": {"paper_only": 0.23, "review_guided": 0.21, "shuffled_review_control": 0.248}, "mean_delta_review_guided_minus_paper_only": -0.02, "mean_delta_review_guided_minus_shuffled_control": -0.038, "delayed_value_case_count": 0, "short_term_positive_long_term_negative_count": 3}, "claim_boundary": "This is a lightweight citation-backed pilot using retrieved Semantic Scholar metadata and simple term-overlap scoring. It is stronger than manual descriptors but still not a full citation graph reconstruction, blinded expert review, or proof of long-term SOTA alignment. It filters citations by lexical relevance, but thin or topically broad citation graphs can still produce misleading frontier terms."}`
- Failure mechanism: Lexical future-frontier scoring can reward terms already present in the original paper and miss review-induced direction changes.
- IGRE design implication: Treat FAVG and citation probes as diagnostics; add semantic and human frontier judgement before declaring long-horizon alignment.

### `semantic_frontier_judge_still_finds_zero_delayed_value_cases`

- Evidence: `{"aggregate": {"paper_count": 5, "successful_judgements": 5, "failed_judgements": 0, "winner_counts": {"paper_context": 4, "review_guided_artifact": 1}, "latent_delayed_value_candidate_count": 0, "semantic_frontier_steering_candidate_count": 0, "mean_scores": {"paper_context": {"semantic_frontier_alignment": 4.2, "actionable_research_control": 4, "novelty_taste_signal": 3.8}, "review_guided_artifact": {"semantic_frontier_alignment": 3.4, "actionable_research_control": 4, "novelty_taste_signal": 3.4}, "best_review_snippet": {"semantic_frontier_alignment": 3, "actionable_research_control": 3.2, "novelty_taste_signal": 2.8}}}, "claim_boundary": "This is a small model-judged semantic probe over citation-derived frontier metadata. It addresses the lexical-overlap limitation but remains model-routed and non-causal; it should be treated as a prioritization signal for future human expert review, not as proof of delayed-value scientific taste."}`
- Failure mechanism: Even a semantic model judge over later-citation metadata can prefer the original paper context when review guidance is generic or underspecified.
- IGRE design implication: Mine and validate delayed-value candidates before expensive replay; generic reviews should not trigger high-cost frontier steering.

### `frontier_metrics_disagree`

- Evidence: `{"case_count": 3, "metric_win_counts": {"internal_review": {"six_gate_hybrid": 3, "raw_review_guided": 0, "tie": 0}, "lexical_frontier": {"six_gate_hybrid": 3, "raw_review_guided": 0, "tie": 0}, "vector_projection": {"six_gate_hybrid": 2, "raw_review_guided": 1, "tie": 0}, "frontier_cosine": {"six_gate_hybrid": 1, "raw_review_guided": 2, "tie": 0}}, "disagreement_rate": 0.6667}`
- Failure mechanism: Internal paper quality, lexical frontier coverage, vector projection, and direct frontier cosine can reward different trajectory movements.
- IGRE design implication: Do not collapse scientific taste into one scalar reward; report direct similarity, trajectory projection, and orthogonal novelty separately.

## Errors

- None

## Claim Boundary

This audit supports failure-mode synthesis and method refinement. It does not convert mixed or negative evidence into superiority evidence for Co-Pilot AI Scientist v3.
