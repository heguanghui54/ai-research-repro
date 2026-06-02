# OpenReview Regeneration Cross-Model Review

- Run ID: `openreview_regeneration_cross_model_review_20260602_081500`
- Source summary: `docs/co_pilot_ai_scientist_v3/experiments/openreview_guided_regeneration_probe_20260602_073500/summary.json`
- Timestamp UTC: `2026-06-02T05:47:51Z`
- Models: `claude-3-7-sonnet-latest`
- Pair count: `6`

## Aggregate

- Review-guided wins: `3`
- Baseline wins: `1`
- Ties: `2`
- Mean delta across models: `0.1667`

## Model Results

| Model | Review-guided wins | Baseline wins | Ties | Mean delta |
| --- | ---: | ---: | ---: | ---: |
| claude-3-7-sonnet-latest | 3 | 1 | 2 | 0.1667 |

## Per-Paper Votes

| Paper ID | Review-guided | Baseline | Tie |
| --- | ---: | ---: | ---: |
| openreview_sample_1 | 1 | 0 | 0 |
| openreview_sample_2 | 1 | 0 | 0 |
| openreview_sample_17 | 1 | 0 | 0 |
| openreview_sample_34 | 0 | 1 | 0 |
| openreview_sample_49 | 0 | 0 | 1 |
| openreview_sample_64 | 0 | 0 | 1 |

## Claim Boundary

Cross-model review reduces same-model scoring bias for regenerated mini-paper artifacts, but it is still model-routed artifact review, not independent human peer review or experiment rerun.
