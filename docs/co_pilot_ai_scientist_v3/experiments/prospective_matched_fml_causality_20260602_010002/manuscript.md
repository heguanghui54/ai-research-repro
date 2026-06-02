# Prospective FML Matched-Budget Pilot Manuscript

Run ID: `prospective_matched_fml_causality_20260602_010002`

## Question

Can Co-Pilot AI Scientist v3 produce a prospective matched-budget package on an
AI Scientist-v2-style FML-bench task, with complete human gate logs and a
matched autonomous baseline?

## Method

Both runs use `Causality_causalml`, model `deepseek-chat`, and
provider `DeepSeek`. The co-pilot package records a
frontier-steering gate over the FML branch frontier. The autonomous baseline is
a separate FML run with the same task and step budget but no human gate.

## Results

| Variant | Validation metric | Test MAE |
| --- | ---: | ---: |
| Co-pilot branch-frontier package | 0.627837 | 0.646224 |
| Autonomous matched baseline | 0.335996 | 0.296399 |

Lower MAE is better. Autonomous-minus-co-pilot test delta: `-0.349825`.

## Claim

This package supports a stronger evidence-shape claim than the controlled
Max-Cut micro-pilot because it uses an AI Scientist-v2-style FML-bench task.
It still does not prove general paper-quality improvement or top-conference
superiority: it is one small task, one model family, and one budget setting.
