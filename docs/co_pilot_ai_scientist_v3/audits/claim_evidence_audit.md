# Claim-Evidence Audit

Audit date: 2026-06-02

This audit keeps the paper aligned with the evidence package. It separates
method contributions, supported empirical claims, negative results, and future
work. The central claim boundary is that IGRE and TFR are reproducible
participation-mode design methods, not yet proof that human-gated automated
science outperforms autonomous AI Scientist-v2 on average.

## Claim Table

| Claim | Evidence | Status | Required paper treatment |
| --- | --- | --- | --- |
| IGRE is a distinct algorithmic pattern for inserting human scientific taste into automated research loops. | Focused EN/ZH papers; `human_gate_schema.json`; gate logs; reusable Codex skill. | Supported as method contribution. | Present as Co-Pilot AI Scientist v3's own five-gate workflow, inspired by prior systems but adapted around human taste, attention cost, and claim calibration. |
| Human scientific taste/insight can be logged as workflow-control metadata rather than generic approval. | `taste_insight_rubric.md/json`; `taste_insight_coverage_audit.md/json`; `human_copilot_trace_dataset.md/json`; attention/taste smoke audits. | Supported as operationalization/readiness evidence. | Claim logging and schema readiness; do not claim population-level live human behavior. |
| Expert peer reviews contain routeable taste/insight signals. | `review_utility_map_probe_20260602_071500`: 473 snippets; 398 actionable; 64 noisy; 245 evaluator-stress, 210 structured-feedback, 140 claim-calibration, 111 taste-prior triggers. | Supported for offline OpenReview proxy. | Treat OpenReview as an offline proxy for human taste, not as real-time co-pilot usage data. |
| Multi-gate routing is structurally useful because review insight is heterogeneous. | Gate-structure ablation: full IGRE utility capture 1.000; best single gate 0.369; random gate mean 0.199; no-gate 0.000. | Supported as routing evidence. | State that this supports gate separation, not downstream paper-quality superiority. |
| Review-to-gate routing is not only a same-sample artifact. | Held-out review-gate validation: train 379 reviews, held-out 94 reviews from 32 papers; full selected policy captures 1.000 held-out utility and routes 0.798 reviews; best single gate captures 0.374; random category mean captures 0.706. | Supported as offline bias-reduction evidence. | Use as held-out stability evidence for deterministic routing, not as independent human labels or downstream paper-quality evidence. |
| Gate routing has downstream association and small causal-style artifact evidence. | Gate-outcome attribution: full IGRE aligned score 75.17 vs best single 37.25; single-gate artifact ablation: best evaluator-stress mean 3.6667 vs full review-guided 3.5 vs baseline 2.9166. | Supported narrowly. | Present as model-reviewed proxy evidence; targeted gates may beat full human context in small settings. |
| Review-guided regeneration can improve some research artifacts. | Six-paper OpenReview regeneration: same-scorer 5/6 wins; Claude cross-review 3 wins, 1 baseline win, 2 ties; equal-context ablation 8 review-guided votes, 1 context-control vote, 3 ties. | Moderately supported by model-reviewed mini-artifacts. | Use "can improve some artifacts"; do not claim human expert validation or real experiment improvement. |
| TFR makes delayed-value human insight measurable. | `temporal_frontier_replay_spec.md/json`; `audit_temporal_frontier_replay.py`; `temporal_frontier_replay_audit.md/json`; citation and semantic frontier probes. | Supported as operationalized protocol. | Present TFR as a falsifiable replay protocol for long-horizon human taste. |
| Historical reviews in the current small OpenReview sample provide positive delayed-value evidence. | Citation-backed probe: 0 delayed-value cases, 3 short-term-positive/long-term-negative cases; review-frontier signal probe: 0 latent delayed-value candidates; semantic frontier judge: 0 delayed-value candidates. | Contradicted / not supported. | Report as negative evidence. The delayed-value hypothesis remains important but unproven. |
| The high-tail hypothesis can be statistically tested rather than used as rhetoric. | `high_tail_power_analysis_20260602_233000`: one-sided Fisher exact test plan; Monte Carlo power table; 5% to 10% tail-rate lift needs roughly 500 matched runs per arm for about 80% power; 5% to 15% needs roughly 150 per arm. | Supported as study-design operationalization. | Present as a future-study requirement and sample-size warning, not as evidence that IGRE already improves breakthrough probability. |
| Short-budget human-gated FML-style runs beat autonomous baselines. | Prospective matched packages: 1 co-pilot/human-selected win vs 3 autonomous/tie/invalid; same-run online FML smokes: 0 co-pilot wins, 1 autonomous win, 1 tie, 1 unknown/no-valid case. | Not supported; mixed or negative. | Keep as failure-mode evidence motivating gate selection, not as superiority evidence. |
| Evaluator-stress gates can prevent metric gaming. | Metric-gaming smoke and FML Fairness replay: primary metric selects degenerate all-negative branch; evaluator-stress gate rejects it and aborts no-valid continuation. | Supported as failure-mode design evidence. | Claim evaluator robustness benefit in controlled/replay settings, not fairness-task improvement. |
| OpenEvolve-style micro-evolution is useful on some machine-gradeable subproblems. | MLAgentBench vectorization: correct 8/8 seeds, median 0.024581 s vs starter 3.261186 s and failed direct rewrite; Max-Cut/knapsack improvements; sklearn diabetes direct rewrite matches OpenEvolve median. | Supported narrowly with boundary conditions. | State that micro-evolution should be triggered selectively, not treated as universal. |
| The package is clean-clone reproducible. | Clean-clone audit: latest audited pushed branch rebuilt four PDFs, validated skill/TFR/gate audits, and found 599/599 manifest artifacts. | Supported for audited commit. | Keep current after each new pushed artifact by refreshing clean-clone audit. |
| The paper is top-conference-ready as empirical proof of co-pilot superiority. | Focused paper reviews and readiness audit show a strong pilot/reproducibility package but remaining gaps: independent human ratings, larger matched tasks/seeds, broader benchmarks. | Not supported. | Present as a promising pilot/system paper package with explicit next evidence requirements. |

## Required Paper Treatment

- Name IGRE and TFR as this paper's own adapted method, not a collage of
  AI Scientist-v2, AI Co-Scientist, AlphaEvolve, and OpenEvolve.
- Emphasize that human participation is high-variance: it can improve rare,
  high-value trajectories while lowering short-budget average metrics.
- Treat OpenReview as a scalable offline proxy for human taste/insight, with
  clear limits relative to real-time co-pilot data.
- Define delayed-value evidence as the temporally asymmetric case where
  review guidance may hurt immediate quality but improve later frontier
  alignment.
- State that no delayed-value positive case has been found in the current
  small sample; this is a negative result and a measurement boundary.
- Treat the high-tail hypothesis as a preregistered large-sample study design:
  current pilots are underpowered for rare breakthrough-probability claims.
- Keep short-budget FML evidence as mixed/negative and use it to justify gate
  selection rather than human-gate superiority.
- Reserve top-conference superiority claims for future work with independent
  human expert ratings and broader matched benchmark runs.

## Remaining Evidence Needed

- Independent human expert ratings for the prepared blind A/B packet.
- Larger matched autonomous vs human-gated runs across tasks and seeds.
- A semantic or expert-judged TFR benchmark that can detect future-direction
  alignment beyond lexical citation overlap.
- Live multi-researcher co-pilot trace data with consent, privacy protection,
  and attention-cost logging.
- Real benchmark reruns where specific review-derived gates alter evaluator
  design, frontier selection, or claim calibration.
