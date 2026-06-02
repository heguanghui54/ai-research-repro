# OpenReview Equal-Context Ablation

- Run ID: `openreview_equal_context_ablation_20260602_142000`
- Source run: `openreview_guided_regeneration_probe_20260602_073500`
- Timestamp UTC: `2026-06-02T06:15:20Z`
- Generation model: `gpt-4o-mini`
- Reviewer models: `gpt-4o-mini, claude-3-7-sonnet-latest`
- Pair count: `6`
- Review-guided wins: `8`
- Context-control wins: `1`
- Ties: `3`
- Mean delta across models: `0.5`

## Design

The earlier OpenReview regeneration probe compared title/abstract-only
artifacts against title/abstract plus real review text. This ablation
controls for extra context by generating a matched-length
`context_control` artifact from unrelated OpenReview snippets. The
reviewers then compare that control with the existing paper-specific
`review_guided` artifact.

## Model Results

| Model | Review-guided wins | Context-control wins | Ties | Mean delta |
| --- | ---: | ---: | ---: | ---: |
| `gpt-4o-mini` | 5 | 1 | 0 | 0.8333 |
| `claude-3-7-sonnet-latest` | 3 | 0 | 3 | 0.1667 |

## Pairwise Votes

- `openreview_sample_1`: review_guided=2, context_control=0, tie=0
- `openreview_sample_2`: review_guided=2, context_control=0, tie=0
- `openreview_sample_17`: review_guided=1, context_control=0, tie=1
- `openreview_sample_34`: review_guided=1, context_control=0, tie=1
- `openreview_sample_49`: review_guided=1, context_control=1, tie=0
- `openreview_sample_64`: review_guided=1, context_control=0, tie=1

## Claim Boundary

This ablation controls for extra context by comparing real paper-specific review guidance against matched-length unrelated review context. It still uses model-routed scoring rather than independent human expert review, and does not rerun the original experiments.
