# Matched Manuscript Quality Score

This is a model-review quality probe over same-continuous-trajectory paired online smoke manuscripts. It is not human expert peer review or top-conference evidence.

## Probe

- Probe ID: `online_full_gate_smoke_20260602_012208_same_continuous`
- Co-pilot manuscript: `docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_012208/online_manuscript/co_pilot_online_full_gate_manuscript.md`
- Autonomous manuscript: `docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_012208/online_manuscript/autonomous_online_comparator_manuscript.md`

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
In this run, A is the co-pilot manuscript and B is the matched
autonomous manuscript. The score should be used only as a
measurement-readiness artifact: a future strong claim requires
multiple tasks, multiple seeds, and independent expert scoring.
