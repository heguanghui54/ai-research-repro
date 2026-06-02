# Autonomous AI Scientist-v2 Baseline on a Matched FML-Bench Pilot

## Abstract

This generated manuscript probe renders the matched autonomous baseline from
`prospective_matched_fml_causality_20260602_000001` as a full paper-shaped manuscript. The baseline uses
the same FML-bench task, model family, tool access, and two-step budget as the
co-pilot package, but it omits human frontier steering. It obtains validation
MAE 0.602170 and test MAE 0.624703, outperforming the co-pilot
package's test MAE 0.646224 under this short-budget setting. The result
supports the autonomous baseline as a necessary negative control, not as a
general proof that autonomous research agents are superior.

## 1. Introduction

A strong human-in-the-loop claim needs a matched autonomous comparator. Without
that comparator, any generated paper can confuse better logging with better
science. This manuscript therefore centers the autonomous path. It asks whether
the same AI Scientist-v2-style execution budget can produce a competitive FML
result without human gate intervention.

## 2. Related Work

The baseline follows the automated research loop used by AI Scientist-v2-style
systems: generate candidate code changes, execute benchmark feedback, keep the
best candidate, and summarize the result. It does not attempt to model human
scientific taste, and it does not include AlphaEvolve/OpenEvolve-style
subproblem escalation.

## 3. Method

The autonomous run receives benchmark instructions and a fixed two-step budget.
It proposes and evaluates candidate changes using `deepseek-chat`
through `DeepSeek`. No human gate selects among branches,
and no attention-cost or taste/insight record is generated. This makes the
baseline less expressive as a scientific collaboration system but cleaner as a
metric-only control.

## 4. Experimental Setup

The task is `Causality_causalml` with metric direction `lower`.
Target files include `causalml/inference/tf/dragonnet.py, causalml/inference/tf/utils.py, split_config.json`.
The baseline primary metric before the short run is
1.296259. The matched co-pilot package
uses the same task, model family, tool access, and step budget.

## 5. Results

| Variant | Validation MAE | Test MAE |
| --- | ---: | ---: |
| Autonomous matched baseline | 0.602170 | 0.624703 |
| IGRE/co-pilot comparator | 0.627837 | 0.646224 |

Lower is better. The autonomous-minus-co-pilot test delta is
-0.021520, so the autonomous run wins on this test metric. This result
is a warning against assuming that human intervention is always positive.

## 6. Claim Audit

Supported: the autonomous baseline is a matched negative control for the FML
prospective package and beats the co-pilot variant on the recorded test MAE.

Unsupported: the baseline does not measure paper quality, novelty, scientific
taste, long-horizon research value, or the chance of rare high-impact
discoveries.

## 7. Limitations

The baseline covers one task and one short budget. It is optimized for the
available scalar metric, so it may miss scientific questions that require
field taste, mechanistic framing, or unusual benchmark choice. A serious
comparison must include multiple tasks, seeds, budgets, and independent paper
quality review.

## 8. Conclusion

The autonomous baseline is strong enough to keep IGRE claims honest. It shows
that under a tight FML budget, removing the human gate can improve the scalar
metric. Future claims for human participation should therefore target upper-tail
scientific value and claim calibration, not average short-run metric gains.
