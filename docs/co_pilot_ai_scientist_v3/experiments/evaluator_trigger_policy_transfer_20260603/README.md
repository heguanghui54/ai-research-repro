# Evaluator-Stress Trigger Policy Transfer

This artifact freezes the trigger policy selected on the discovery split
package and evaluates the same policy on held-out split seeds. It is a
stricter check than choosing the best policy independently inside each
package.

## Selection

- Train package: `prospective_matched_open_data_multitask_20260603`
- Held-out package: `prospective_matched_open_data_multitask_holdout_20260603`
- Selection rule: Choose the discovery-split policy with maximum mean delta versus autonomous selection, breaking ties by fewer autonomous losses and then fewer trigger events.
- Frozen selected policy: `class_imbalance_trigger_0_94`

## Results

| Condition | Mean test balanced accuracy | Delta vs autonomous | Wins | Losses | Ties | Triggered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train frozen policy | 0.927934 | 0.003077 | 2 | 0 | 23 | 5 |
| held-out autonomous | 0.920681 | 0.000000 | 0 | 0 | 25 | 0 |
| held-out always-on evaluator-stress | 0.923263 | 0.002582 | 2 | 2 | 21 | 4 |
| held-out frozen policy | 0.924320 | 0.003639 | 2 | 0 | 23 | 5 |

## Transfer Interpretation

The discovery split selects `class_imbalance_trigger_0_94`. When frozen and evaluated on held-out split seeds, the policy obtains delta `0.003639444256184343` against autonomous selection with `2` wins, `0` losses, and `23` ties. The always-on gate has `2` held-out losses.

## Claim Boundary

This is a discovery-to-held-out split validation inside one open-data task family. It supports trigger-conditioned evaluator-stress design, not broad co-pilot superiority or a universally optimal threshold.
