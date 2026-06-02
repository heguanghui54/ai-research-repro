# Prospective Attention and Taste/Insight Cost Audit

- Audit date: `2026-06-02T19:27:18Z`
- Status: `pass`
- Prospective packages: `7`
- Gate records: `7`
- Complete attention-cost gates: `7/7`
- Complete taste/insight gates: `7/7`
- Total active review minutes: `21.00`
- Total wall-clock latency minutes: `21.00`
- Mean taste/insight score: `3.447`

## Gate Types

| Gate type | Count |
| --- | --- |
| `evaluator_stress_test` | `2` |
| `frontier_steering` | `5` |

## Per-Gate Records

| Package | Gate | Active min | Options | Taste score | Factors |
| --- | --- | ---: | ---: | ---: | --- |
| `prospective_matched_fml_causality_20260602_000001` | `frontier_steering` | `3.0` | `2` | `3.57` | ai-scientist-v2-trajectory-relevance, negative-results-still-informative |
| `prospective_matched_fml_causality_20260602_010002` | `frontier_steering` | `3.0` | `2` | `3.57` | ai-scientist-v2-trajectory-relevance, negative-results-still-informative |
| `prospective_matched_fml_fairness-fairlearn_20260602_002821` | `frontier_steering` | `3.0` | `2` | `3.57` | ai-scientist-v2-trajectory-relevance, negative-results-still-informative |
| `prospective_matched_micro_pilot_20260602_000001` | `frontier_steering` | `2.0` | `2` | `3.14` | mechanistic-branch-interpretability, package-shape-validation |
| `prospective_matched_micro_pilot_20260603_ssh_maxcut` | `frontier_steering` | `2.0` | `2` | `3.14` | mechanistic-branch-interpretability, package-shape-validation |
| `prospective_matched_open_data_multitask_20260603` | `evaluator_stress_test` | `4.0` | `2` | `3.57` | evaluator-validity, class-balance-risk, open-data-reproducibility |
| `prospective_matched_open_data_multitask_holdout_20260603` | `evaluator_stress_test` | `4.0` | `2` | `3.57` | evaluator-validity, class-balance-risk, open-data-reproducibility |

## Errors

- None

## Warnings

- None

## Claim Boundary

This audit supports prospective operator-recorded attention and taste/insight measurement across the matched-budget packages. It is not independent human-subject evidence, does not estimate population-level attention cost, and does not prove that human gates improve paper quality.
