# Held-Out Review-Gate Validation

Run date: 2026-06-02T09:56:38Z

## Purpose

This probe checks whether OpenReview-derived gate routing is stable on
held-out papers. Categories are selected on the train split only, then
evaluated on held-out reviews. This reduces sample-reuse bias in the
review-to-gate evidence, although it is still an offline deterministic
proxy rather than independent human expert validation.

## Split

- Train reviews: `379`
- Held-out reviews: `94`
- Held-out rule: `paper_index % 5 == 4`

## Selected Categories

- `actionable_suggestion` -> `structured_feedback`
- `clarity_presentation` -> `structured_feedback`
- `evaluation_metric` -> `evaluator_stress_test`
- `limitations_claim_boundary` -> `claim_calibration`
- `method_correctness` -> `evaluator_stress_test`
- `novelty_positioning` -> `scientific_taste_prior`
- `reproducibility_detail` -> `structured_feedback`

## Held-Out Results

| Policy | Utility capture rate | Routed review rate | Noisy-only route rate |
| --- | ---: | ---: | ---: |
| Full selected policy | 1.000 | 0.798 | 0.000 |
| Best single-gate policy | 0.374 | 0.521 | 0.000 |
| Random category baseline mean | 0.706 | 0.700 | n/a |
| No-gate baseline | 0.000 | 0.000 | 0.000 |

## Claim Boundary

Held-out validation supports stability of deterministic OpenReview-to-gate routing under a paper-level split. It does not provide independent human labels, does not prove downstream paper-quality improvement, and should be treated as an offline bias-reduction check for the review-derived gate policy.
