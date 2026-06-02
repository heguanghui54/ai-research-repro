# Autonomous AI Scientist-v2 Manuscript Comparator for an Online IGRE Smoke

## Abstract

This manuscript is generated from an autonomous AI Scientist-v2 summary used as
a matched-budget comparator for the online IGRE trajectory
`online_full_gate_smoke_20260602_010521`. The autonomous run uses benchmark
`Causality_causalml`, model `deepseek-chat`,
provider `DeepSeek`, and `2`
AI Scientist-v2 step(s) without human gate interventions. Its best validation
metric is `0.621262` and its held-out
primary test metric is `0.640451`. The
co-pilot online trajectory's selected continuation test metric is
`0.862015`. Lower is better for this
Causality MAE task. This comparator is useful for manuscript-quality
measurement, but it is not a same-continuous-trajectory autonomous run.

## 1. Introduction

A co-pilot research system should be compared against an autonomous agent that
receives similar task, model, and budget constraints. This generated manuscript
therefore renders the autonomous side of the evidence rather than treating the
co-pilot manuscript in isolation. The goal is not to make the autonomous
baseline look weak; it is to expose whether human-gated evidence packaging and
claim calibration add value when the benchmark metric may favor the autonomous
run.

## 2. Method

The autonomous comparator runs AI Scientist-v2 on `Causality_causalml`
without idea, evaluator, branch, program-search, or claim gates. It relies on
the standard agent loop to propose and edit code, evaluate validation metrics,
and select the best available snapshot. The source summary is
`docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/autonomous_baseline_summary.json`.

## 3. Experimental Setup

| Quantity | Value |
| --- | --- |
| Benchmark | `Causality_causalml` |
| Model/provider | `deepseek-chat` / `DeepSeek` |
| Metric | `mae_mean` |
| Direction | `lower` |
| Baseline metric | `1.296259` |
| AI Scientist-v2 steps | `2` |

The co-pilot trajectory used for comparison is
`online_full_gate_smoke_20260602_010521`. Its FML component selects a branch with
validation MAE `0.621461` and reports
held-out test MAE `0.862015`.

## 4. Results

| Path | Validation metric | Test primary metric |
| --- | ---: | ---: |
| Co-pilot online trajectory | 0.621461 | 0.862015 |
| Autonomous comparator | 0.621262 | 0.640451 |

The autonomous comparator provides a real negative check on broad co-pilot
claims whenever it matches or exceeds the co-pilot metric. In the current
comparison, the autonomous test metric is `0.640451`
and the co-pilot online trajectory's test metric is
`0.862015`.

## 5. Claim Audit

Supported:

- A manuscript comparator can be generated from an autonomous AI Scientist-v2
  summary using the same evidence-bound template family as the co-pilot online
  manuscript.
- The autonomous result gives an explicit benchmark counterweight to the
  human-gated manuscript.

Unsupported:

- The comparator is not a same-continuous-trajectory autonomous manuscript
  generated inside the exact online orchestration run.
- The comparator does not measure human scientific taste or attention cost.
- The comparator does not by itself establish paper-quality superiority for
  either condition.

## 6. Limitations

This is a matched-budget manuscript comparator, not a fully matched online
trajectory pair. The autonomous summary may come from a nearby prospective
package rather than from the same orchestrator invocation as the co-pilot
trajectory. Stronger evidence requires launching a paired autonomous trajectory
beside the fresh co-pilot trajectory and independently reviewing both full
manuscripts.

## 7. Conclusion

The autonomous manuscript comparator makes the online manuscript probe more
scientifically useful: the co-pilot paper artifact is no longer judged only
against itself. The result remains a pilot measurement artifact and should be
reported as such.
