# Evaluator-Stress Trigger Policy Analysis

This analysis uses the archived multi-seed open-data pilot to test whether
the evaluator-stress gate should be always on or triggered only when the
validation data indicate evaluator risk.

## Aggregate Policy Results

| Policy | Mean test balanced accuracy | Delta vs autonomous | Wins | Losses | Ties | Triggered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `autonomous_accuracy_only` | 0.924857 | 0.000000 | 0 | 0 | 25 | 0 |
| `always_on_evaluator_stress` | 0.926426 | 0.001569 | 2 | 2 | 21 | 4 |
| `class_imbalance_trigger_0_90` | 0.927934 | 0.003077 | 2 | 0 | 23 | 10 |
| `class_imbalance_trigger_0_94` | 0.927934 | 0.003077 | 2 | 0 | 23 | 5 |
| `validation_balanced_gap_trigger_0_02` | 0.926395 | 0.001538 | 1 | 0 | 24 | 1 |
| `hybrid_imbalance_or_gap_trigger` | 0.927934 | 0.003077 | 2 | 0 | 23 | 10 |

Best policy by mean delta with loss/trigger parsimony tie-breaks: `class_imbalance_trigger_0_94`.

## Best Policy Dataset Summary

| Dataset | Splits | Delta vs autonomous | Wins | Losses | Ties | Triggered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| breast_cancer | 5 | 0.000000 | 0 | 0 | 5 | 0 |
| digits | 5 | 0.000000 | 0 | 0 | 5 | 0 |
| digits_zero_vs_rest | 5 | 0.000000 | 0 | 0 | 5 | 0 |
| synthetic_imbalanced_stress | 5 | 0.015385 | 2 | 0 | 3 | 5 |
| wine | 5 | 0.000000 | 0 | 0 | 5 | 0 |

## Interpretation

The always-on evaluator-stress gate is mixed: it improves the synthetic imbalance stress case but creates small overreach losses on breast cancer. A class-imbalance trigger based on the validation majority baseline keeps the imbalance benefit while avoiding those clean-task losses in this pilot.

## Claim Boundary

This is a post-hoc trigger-policy analysis over one archived pilot. It supports a design rule for future prospective evaluator gates, not a broad performance claim.
