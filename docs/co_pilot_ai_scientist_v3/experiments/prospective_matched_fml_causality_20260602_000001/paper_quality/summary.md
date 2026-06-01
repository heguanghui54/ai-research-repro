# Matched Mini-Manuscript Quality Score

This is a narrow quality probe over two mini-manuscripts from one
prospective matched-budget package. It is not evidence that the full
Co-Pilot AI Scientist v3 system writes better papers.

## Package

- Package: `prospective_matched_fml_causality_20260602_000001`
- Co-pilot manuscript: `docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_fml_causality_20260602_000001/manuscript.md`
- Autonomous manuscript: `docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_fml_causality_20260602_000001/autonomous_manuscript.md`

## Aggregate

- Successful reviewer calls: 2/2
- Co-pilot manuscript wins: 2
- Autonomous manuscript wins: 0
- Ties: 0

## Reviewer Results

| Model | Status | Recommendation | A overall | B overall | Interpretation |
| --- | ---: | --- | ---: | ---: | --- |
| `gpt-4o-mini` | 200 | A | 4 | 3 | co_pilot_preferred |
| `claude-3-7-sonnet-latest` | 200 | A | 4 | 3 | co_pilot_preferred |

## Interpretation

The manuscripts are intentionally anonymized as A and B during scoring.
In this run, A is the co-pilot package manuscript and B is the matched
autonomous baseline manuscript. The score should be used only as a
measurement-readiness artifact: a future strong claim requires full
manuscripts from complete end-to-end trajectories, multiple tasks, and
independent expert scoring.
