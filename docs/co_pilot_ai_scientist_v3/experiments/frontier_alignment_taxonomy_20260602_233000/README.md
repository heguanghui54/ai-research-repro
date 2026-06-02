# Frontier Alignment Taxonomy

This artifact operationalizes the user's point that regenerated research should be compared with current frontier directions, not only with local experiment scores.

## Sources

- `ICLR 2025`: https://blog.iclr.cc/2025/04/22/announcing-the-outstanding-paper-awards-at-iclr-2025/
- `ICML 2025`: https://icml.cc/virtual/2025/awards_detail
- `ACL 2025`: https://2025.aclweb.org/program/awards/

## Frontier Dimensions

- `alignment_safety_reliability` (weight `1.15`): alignment, safety, refusal, reliability, robust, compression, privacy, unlearning
- `mechanistic_theoretical_insight` (weight `1.1`): theory, mechanistic, dynamics, representation, geometry, proof, causal, understanding
- `efficient_systems_and_inference` (weight `1.0`): efficient, efficiency, inference, sparse, hardware, speculative, latency, training run
- `adaptive_long_horizon_search` (weight `1.2`): planning, adaptive, long-horizon, creative, frontier, search, hypothesis, collaboration
- `evaluation_benchmark_shift` (weight `1.05`): benchmark, evaluation, measurement, metric, dataset, stress, audit, traceability
- `deployment_and_social_value` (weight `0.9`): welfare, fairness, medical, equity, deployment, global, human-centered, policy

## Deep Case Alignment Results

- Six-gate hybrid wins: `3/3`
- Raw review-guided wins: `0/3`
- Ties: `0/3`
- Mean delta, six-gate minus raw: `3.467`

| Case | Raw score | Six-gate score | Delta | Winner |
| --- | ---: | ---: | ---: | --- |
| `openreview_sample_1` | 12.45 | 17.1 | 4.65 | `six_gate_hybrid` |
| `openreview_sample_17` | 12.6 | 16.05 | 3.45 | `six_gate_hybrid` |
| `openreview_sample_2` | 6.85 | 9.15 | 2.3 | `six_gate_hybrid` |

## Boundary

This is a deterministic lexical frontier-alignment proxy seeded from a small official award-paper sample. It is useful for measurement design, not a substitute for citation-based frontier modeling or expert judgement.
