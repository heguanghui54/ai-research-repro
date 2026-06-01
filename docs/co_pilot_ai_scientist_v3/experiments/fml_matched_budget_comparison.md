# FML-Bench Matched-Budget Branch-Gate Comparison

This comparison addresses the strongest paper-quality review blocker: the
selected-branch continuation needed same-budget autonomous AI Scientist-v2
baselines. It now contains two matched Causality replicates rather than a single
positive pilot.

## Setup

- Benchmark: `Causality_causalml`
- Model/provider: `deepseek-chat` through `DeepSeek`
- Metric: IHDP test `mae_mean`, lower is better
- Human-gated path:
  - two initial draft branches;
  - branch gate selects draft 2;
  - two-step continuation from the selected snapshot.
- Autonomous matched baseline:
  - four total AI Scientist-v2 steps;
  - two initial ideas, two parallel branches;
  - no human branch selection;
  - stage budgets `[0.5, 0.5, 0.0, 0.0]`.

## Pair 1 Results

| Variant | Total steps | Best validation MAE | Test MAE | Notes |
| --- | ---: | ---: | ---: | --- |
| Human-gated initial two drafts | 2 | 0.621262 | 0.640451 | Produces the branch frontier. |
| Human-gated selected continuation | 4 total | 0.401240 | 0.402170 | Two draft steps plus two continuation steps from selected draft 2. |
| Autonomous matched 4-step baseline | 4 | 0.389451 | 0.421474 | Stronger validation metric but slightly worse held-out test metric. |

Pair 1 weakly favors the human-gated continuation on held-out test MAE
(`0.402170` vs. `0.421474`) while the autonomous run has a slightly better
validation MAE (`0.389451` vs. `0.401240`).

## Pair 2 Results

| Variant | Total steps | Best validation MAE | Test MAE | Notes |
| --- | ---: | ---: | ---: | --- |
| Human-gated initial two drafts | 2 | 0.605881 | 0.646224 | Produces the branch frontier; step 2 selected. |
| Human-gated selected continuation | 4 total | 0.627837 | 0.646224 | Continuation did not improve the selected frontier. |
| Autonomous matched 4-step baseline | 4 | 0.537972 | 0.595685 | Better validation and held-out test metric. |

Pair 2 favors the autonomous baseline on held-out test MAE (`0.595685` vs.
`0.646224`). This is important negative evidence: the branch gate and
snapshot-seeded continuation do not reliably improve the FML Causality outcome
under the tiny matched budget used here.

## Aggregate Interpretation

Across the two paired Causality replicates, one pair favors the human-gated
path and one pair favors the autonomous path on held-out test MAE. The mean
human-gated test MAE is `0.524197`; the mean autonomous test MAE is `0.508579`.
Because lower is better, the two-pair mean slightly favors the autonomous
baseline by `0.015618`.

This reduces an important compute-budget confound, but the evidence is mixed.
The current paper should therefore claim feasibility of branch-gate insertion
and selected-snapshot continuation, not general human-gate superiority.

## Remaining Caveats

- One benchmark task family only; two paired replicates are still too few for a
  statistical claim.
- The human-gated continuation uses snapshot seeding rather than native tree
  object resume.
- The autonomous baseline uses a compact four-step budget schedule; further
  runs should test additional budget schedules.
- Human attention cost is still estimated from logs rather than measured with a
  live human timer.

## Artifact Paths

- Human-gated drafts: `fml_online_branch_gate_drafts/`
- Human-gated continuation: `fml_selected_branch_continuation/`
- Autonomous matched baseline: `fml_autonomous_matched_budget_4step/`
- Pair 2 human-gated drafts: `fml_matched_budget_rep2_gated_drafts/`
- Pair 2 human-gated continuation:
  `fml_matched_budget_rep2_selected_continuation/`
- Pair 2 autonomous matched baseline:
  `fml_matched_budget_rep2_autonomous_4step/`
