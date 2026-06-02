# Prospective FML Matched-Budget Pilot Manuscript

Run ID: `prospective_matched_fml_fairness-fairlearn_20260602_002821`

## Question

Can Co-Pilot AI Scientist v3 produce a prospective matched-budget package on
the AI Scientist-v2-style FML-bench task `configs/tasks/fairness_fairlearn.yaml`, with complete human
gate logs and a matched autonomous baseline?

## Method

Both runs use `configs/tasks/fairness_fairlearn.yaml`, model `deepseek-chat`, and
provider `DeepSeek`. The co-pilot package records a
frontier-steering gate over the FML branch frontier. The autonomous baseline is
a separate FML run with the same task and step budget but no human gate.

## Results

| Variant | Validation metric | Test primary_metric |
| --- | ---: | ---: |
| Co-pilot branch-frontier package | NA | NA |
| Autonomous matched baseline | 0.190321 | 0.172152 |

Lower primary_metric is better.
Autonomous-minus-co-pilot test delta: `NA`.

## Claim

This package supports a stronger evidence-shape claim than the controlled
Max-Cut micro-pilot because it uses an AI Scientist-v2-style FML-bench task.
It still does not prove general paper-quality improvement or top-conference
superiority: it is one small task, one model family, and one budget setting.
