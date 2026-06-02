# Gate-Structure Ablation Probe

- Run ID: `gate_structure_ablation_probe_20260602_183000`
- Status: `pass`
- Source: `docs/co_pilot_ai_scientist_v3/experiments/review_utility_map_probe_20260602_071500/scored_reviews.json`
- Review snippets: `473`
- Actionable snippets: `398`
- Best policy by utility capture: `full_igre`

## Policy Scores

| Policy | Captured utility | Utility capture | Actionable coverage | High-utility coverage | Low-score actionable coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| `no_gate` | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| `single_scientific_taste_prior` | 555 | 0.148435 | 0.278894 | 0.420732 | 0.253623 |
| `single_evaluator_stress_test` | 1380 | 0.369083 | 0.615578 | 0.865854 | 0.666667 |
| `single_frontier_steering` | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| `single_structured_feedback` | 1104 | 0.295266 | 0.527638 | 0.542683 | 0.521739 |
| `single_claim_calibration` | 700 | 0.187216 | 0.351759 | 0.579268 | 0.340580 |
| `full_igre` | 3739 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| `random_gate_mean_128_seeds` | 743.00 | 0.198716 | 0.353702 | 0.480898 | 0.350487 |

## Interpretation

On the archived OpenReview-derived review-utility map, full IGRE captures all routed actionable signal by construction, while no-gate captures none. Among single gates, single_evaluator_stress_test captures the most utility, but it misses review signals routed to the other gate types. The random-gate baseline captures only a fraction of the available utility on average. This supports the architectural reason for multiple explicit gates: expert-review signals are heterogeneous and should not be compressed into one approval step.

## Claim Boundary

This is a deterministic routing ablation over archived OpenReview-derived review snippets. It supports the need for a multi-gate logging and routing structure, but it does not prove downstream paper-quality improvement, benchmark superiority, or independent human-review validity.
