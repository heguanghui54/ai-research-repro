# FML-Bench Matched-Budget Branch-Gate Comparison

This comparison addresses the strongest paper-quality review blocker: the
selected-branch continuation needed a same-budget autonomous AI Scientist-v2
baseline.

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

## Results

| Variant | Total steps | Best validation MAE | Test MAE | Notes |
| --- | ---: | ---: | ---: | --- |
| Human-gated initial two drafts | 2 | 0.621262 | 0.640451 | Produces the branch frontier. |
| Human-gated selected continuation | 4 total | 0.401240 | 0.402170 | Two draft steps plus two continuation steps from selected draft 2. |
| Autonomous matched 4-step baseline | 4 | 0.389451 | 0.421474 | Stronger validation metric but slightly worse held-out test metric. |

The single-task matched comparison weakly favors the human-gated continuation on
held-out test MAE (`0.402170` vs. `0.421474`) while the autonomous run has a
slightly better validation MAE (`0.389451` vs. `0.401240`). This reduces an
important compute-budget confound, but it does not yet prove that human gating
generally improves AI Scientist-v2.

## Remaining Caveats

- One task and one seed only.
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
