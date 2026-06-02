# Insight-Gated Research Evolution on a Matched FML-Bench Pilot

## Abstract

This generated manuscript probe renders the prospective package
`prospective_matched_fml_fairness-fairlearn_20260602_002821` as a full paper-shaped IGRE/co-pilot manuscript.
The system inserts a human frontier-steering gate into an AI Scientist-v2-style
FML-bench run, records attention cost and scientific taste/insight, and compares
the selected branch with a matched autonomous baseline on `configs/tasks/fairness_fairlearn.yaml`.
The co-pilot frontier did not produce a valid scored continuation, so the correct scientific action is to abort the branch rather than over-interpret a broken candidate. The autonomous baseline obtains validation
primary_metric 0.190321 and test primary_metric
0.172152. Since lower is better, the test delta
autonomous-minus-co-pilot is n/a. The contribution is therefore
evidence of a reproducible human-gated research trajectory format, not evidence
that human gates improve average performance.

## 1. Introduction

Automated AI research systems can run idea generation, code editing, benchmark
execution, and draft writing with limited human involvement. IGRE asks a
different question: where should a human scientist intervene when the valuable
signal is not fully captured by a scalar metric? In this package, the human
gate is not treated as a guaranteed improvement. It is treated as a
high-variance search intervention that may sometimes hurt average short-budget
metrics but can preserve scientific taste, unusual problem selection, and
claim responsibility.

The manuscript is generated from archived artifacts rather than a fresh online
trajectory. That distinction matters: it can test whether the package contains
enough evidence to write a complete, calibrated manuscript, but it cannot prove
that the whole system autonomously produced a top-conference paper.

## 2. Related Work

The run is inspired by AI Scientist-v2-style benchmark execution and paper
writing, AI Co-Scientist-style hypothesis organization, and AlphaEvolve-style
program evolution. The method here is not a direct copy of those systems. IGRE
renames and adapts the process around four paper-specific requirements:
frontier steering, taste/insight logging, evaluator stress testing, and claim
calibration. Because official AlphaEvolve core code is unavailable, the broader
package uses OpenEvolve only as an AlphaEvolve-style substrate for reproducible
program-search subproblems.

## 3. Method

IGRE represents the research process as a gated trajectory. Automated agents
produce candidate branches, evaluators score them, and selected human gates may
intervene when scalar metrics are too narrow. Each gate records candidate
options, the chosen branch, a rationale, attention cost, and scientific
taste/insight fields. The goal is not to convert taste into a hidden reward
model. The goal is to make normally tacit scientific judgment auditable enough
to compare against autonomous baselines.

For this FML package, the key gate is:

> The frontier gate reviewed 2 candidate branches (no numerically scored options) and selected `abort_no_valid_branch`. The recorded active review time is 3.0 minutes, and the taste/insight score is 3.57. The qualitative rationale is: The branch choice is scientifically modest but claim-relevant: configs/tasks/fairness_fairlearn.yaml directly tests whether frontier steering can be inserted into an AI Scientist-v2 benchmark trajectory.

## 4. Experimental Setup

Both variants use `Fairness_fairlearn`, model
`deepseek-chat`, provider `DeepSeek`, and the same
two-step budget. The co-pilot path first samples two frontier branches and
continues the selected one. The autonomous baseline receives the same task,
model family, tool access, and step budget but no human gate. The metric is
`primary_metric` on the FML benchmark; lower is better.

## 5. Results

| Variant | Validation primary_metric | Test primary_metric |
| --- | ---: | ---: |
| IGRE/co-pilot selected branch | n/a | n/a |
| Matched autonomous baseline | 0.190321 | 0.172152 |

If the co-pilot score is `n/a`, the autonomous baseline is the only valid
tested path in this package. Otherwise, the table should be read according to
the metric direction above. This negative or invalid-branch result is useful:
it prevents the manuscript from claiming that a human gate is automatically
beneficial under tight budgets. The positive result is narrower: the package
demonstrates that a prospective, matched-budget, human-gated AI
Scientist-v2-style evidence bundle can be produced, audited, and aborted when
the frontier contains no valid continuation.

## 6. Claim Audit

Supported: the package contains a prospective co-pilot trajectory, matched
autonomous baseline, complete human gate record, final claim audit, and
manuscript artifact.

Unsupported: this run does not show that human gates improve average benchmark
performance, human attention efficiency, or full paper quality. It also does
not establish top-conference empirical support.

## 7. Limitations

The run covers one FML task, one model family, one short budget, and one
human-gate decision. When the co-pilot frontier has no valid scored
continuation, the scientific-taste intervention mainly tests failure
recognition and claim discipline, not metric superiority. Independent expert
review and multi-task, multi-seed matched comparisons remain necessary.

## 8. Conclusion

This probe supports IGRE as a distinctive, reproducible co-pilot pattern for
making human scientific taste and attention cost visible inside AI research
loops. It should be presented as pilot evidence and manuscript-readiness
evidence, not as proof that co-pilot systems outperform autonomous AI
Scientist-v2.
