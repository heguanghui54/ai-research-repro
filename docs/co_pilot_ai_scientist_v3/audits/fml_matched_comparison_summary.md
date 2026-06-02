# FML Matched-Comparison Summary

This is a machine-generated summary of archived FML matched-budget
comparisons. It separates the formal two-pair Causality replicate from
the smaller online-smoke comparison.

## Formal Four-Step Causality Pairs

| Pair | Human-gated test MAE | Autonomous test MAE | Autonomous - human | Winner |
| --- | ---: | ---: | ---: | --- |
| `causality_pair_1` | 0.402170 | 0.421474 | 0.019303 | human_gated |
| `causality_pair_2` | 0.646224 | 0.595685 | -0.050539 | autonomous_or_tie |

## Formal Aggregate

- Formal pair count: 2
- Human-gated mean test MAE: `0.524197`
- Autonomous mean test MAE: `0.508579`
- Mean autonomous-minus-human delta: `-0.015618`
- Delta SEM: `0.034921`
- Human-gated wins: 1
- Autonomous/tie wins: 1
- Statistical claim: `not_supported_n_too_small`

Because lower MAE is better, the negative mean delta means the two-pair
mean slightly favors the autonomous baseline. With only two formal
pairs, this is underpowered evidence and should not be presented as a
stable performance conclusion.

## Online Smoke Comparison

| Comparison | Human-gated test MAE | Autonomous test MAE | Autonomous - human | Winner |
| --- | ---: | ---: | ---: | --- |
| `online_smoke_matched_autonomous_3step_001` | 0.862015 | 0.428516 | -0.433500 | autonomous_or_tie |

## Prospective Two-Step FML Packages

| Package | Co-pilot test MAE | Autonomous test MAE | Autonomous - human | Winner |
| --- | ---: | ---: | ---: | --- |
| `prospective_matched_fml_causality_20260602_000001` | 0.646224 | 0.624703 | -0.021520 | autonomous_or_tie |
| `prospective_matched_fml_causality_20260602_010002` | 0.646224 | 0.296399 | -0.349825 | autonomous_or_tie |

## Prospective Two-Step Aggregate

- Package count: 2
- Human-gated wins: 0
- Autonomous/tie wins: 2
- Mean autonomous-minus-human delta: `-0.185672`
- Delta SEM: `0.164152`
- Statistical claim: `not_supported_n_too_small`

## Claim Implication

The formal FML Causality pairs are mixed and slightly favor autonomous on the two-pair mean. The prospective two-step FML packages and the online smoke comparison are also negative for co-pilot performance. These artifacts support branch-gate feasibility and evidence discipline, not superiority.
