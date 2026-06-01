# Autonomous FML Matched-Budget Pilot Manuscript

Run ID: `prospective_matched_fml_causality_20260602_000001`

## Question

Can an autonomous AI Scientist-v2 run produce a matched-budget baseline on the
same FML-bench task used by the Co-Pilot AI Scientist v3 prospective package?

## Method

This baseline uses `Causality_causalml`, model
`deepseek-chat`, provider `DeepSeek`,
and the same two-step budget recorded in the matched package manifest. It does
not include a human frontier-steering gate or taste/attention log.

## Results

| Variant | Validation metric | Test MAE |
| --- | ---: | ---: |
| Autonomous matched baseline | 0.602170 | 0.624703 |
| Co-pilot package comparator | n/a | 0.646224 |

Lower MAE is better. In this package, the autonomous baseline has the lower
test MAE.

## Claim

This baseline supports a negative control for the co-pilot package: under the
same task, model family, tool access, and step budget, the autonomous run does
better on the held-out test metric. It does not evaluate human scientific taste,
attention efficiency, or paper quality; it only supplies a matched benchmark
and manuscript comparator for the current prospective pilot.
