# Autonomous AI Scientist-v2 Manuscript Comparator for an Online IGRE Smoke

## Abstract

This manuscript is generated from an autonomous AI Scientist-v2 summary used as
a matched-budget comparator for the online IGRE trajectory
`online_full_gate_smoke_20260602_013612`. The autonomous run uses benchmark
`Fairness_fairlearn`, model `deepseek-chat`,
provider `DeepSeek`, and `1`
AI Scientist-v2 step(s) without human gate interventions. Its best validation
metric is `n/a` and its held-out
primary test metric is `n/a`. The
co-pilot online trajectory's selected continuation test metric is
`n/a`. Lower is better for this
Causality MAE task. This comparator is useful for manuscript-quality
measurement as a same-continuous-trajectory autonomous baseline.

## 1. Introduction

A co-pilot research system should be compared against an autonomous agent that
receives similar task, model, and budget constraints. This generated manuscript
therefore renders the autonomous side of the evidence rather than treating the
co-pilot manuscript in isolation. The goal is not to make the autonomous
baseline look weak; it is to expose whether human-gated evidence packaging and
claim calibration add value when the benchmark metric may favor the autonomous
run.

## 2. Method

The autonomous comparator runs AI Scientist-v2 on `Fairness_fairlearn`
without idea, evaluator, branch, program-search, or claim gates. It relies on
the standard agent loop to propose and edit code, evaluate validation metrics,
and select the best available snapshot. The source summary is
`docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_013502/autonomous_baseline_summary.json`.

## 3. Experimental Setup

| Quantity | Value |
| --- | --- |
| Benchmark | `Fairness_fairlearn` |
| Model/provider | `deepseek-chat` / `DeepSeek` |
| Metric | `abs_demographic_parity_diff_mean` |
| Direction | `lower` |
| Baseline metric | `0.186632` |
| AI Scientist-v2 steps | `1` |

The co-pilot trajectory used for comparison is
`online_full_gate_smoke_20260602_013612`. Its FML component selects a branch with
validation MAE `n/a` and reports
held-out test MAE `n/a`.

## 4. Results

| Path | Validation metric | Test primary metric |
| --- | ---: | ---: |
| Co-pilot online trajectory | n/a | n/a |
| Autonomous comparator | n/a | n/a |

The autonomous comparator provides a real negative check on broad co-pilot
claims whenever it matches or exceeds the co-pilot metric. In the current
comparison, the autonomous test metric is `n/a`
and the co-pilot online trajectory's test metric is
`n/a`.

## 5. Claim Audit

Supported:

- A manuscript comparator can be generated from an autonomous AI Scientist-v2
  summary using the same evidence-bound template family as the co-pilot online
  manuscript.
- The autonomous result gives an explicit benchmark counterweight to the
  human-gated manuscript.

Unsupported:

- The comparator is only one tiny-budget same-continuous-trajectory run.
  It does not establish general performance or paper-quality superiority.
- The comparator does not measure human scientific taste or attention cost.
- The comparator does not by itself establish paper-quality superiority for
  either condition.

## 6. Limitations

This is a same-continuous-trajectory manuscript comparator, but only a tiny-budget smoke. Stronger evidence requires repeating paired trajectories across tasks and seeds and independently reviewing both full manuscripts.

## 7. Conclusion

The autonomous manuscript comparator makes the online manuscript probe more
scientifically useful: the co-pilot paper artifact is no longer judged only
against itself. The result remains a pilot measurement artifact and should be
reported as such.
