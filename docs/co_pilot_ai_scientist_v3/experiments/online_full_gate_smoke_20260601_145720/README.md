# Online Full-Gate Smoke Trajectory

- Trajectory ID: `online_full_gate_smoke_20260601_145908`
- Generated at: `2026-06-01T14:59:08Z`
- Remote host: `ubuntu-heshi`
- Remote root: `/home/heshi/work/copilotv3-online-full-gate-smoke-20260601_145720`
- Single online smoke run: `True`

This is a fresh online smoke trajectory that exercises all five gate types and launches remote FML-bench plus OpenEvolve work. It proves orchestration feasibility, not general performance superiority.

Environment note: an earlier attempt on the same day failed before scoring
because the remote `causalml` environment had NumPy 2.x while TensorFlow 2.10
required a NumPy 1.x ABI. The environment was repaired on `ubuntu-heshi` by
installing `numpy<2`; the successful run below used NumPy 1.26.4 and TensorFlow
2.10.0.

## Summary

| Metric | Value |
| --- | ---: |
| `selected_research_direction` | `hitl-gated-tree-search` |
| `selected_branch` | `step_0002` |
| `selected_branch_val_mae` | 0.627837 |
| `continuation_test_mae` | 0.862015 |
| `program_search_best_score` | 1.000000 |
| `branch_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260601_145720/branch_frontier/ai_scientist_v2/Causality_causalml/20260601_225725_4ab98f3d/summary.json` |
| `continuation_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260601_145720/selected_continuation/ai_scientist_v2/Causality_causalml/20260601_225913_27109cec/summary.json` |
| `program_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260601_145720/program_search/knapsack_openevolve_1iter/summary.json` |

## Gate Decisions

### idea_gate_online_smoke_001

- Type: `idea_selection`
- Decision: `hitl-gated-tree-search`
- Rationale: Use the currently selected narrow contribution as the online smoke trajectory target.

### evaluator_gate_online_smoke_001

- Type: `evaluator_approval`
- Decision: `causality_mae_plus_guardrails`
- Rationale: Approve a low-cost evaluator bundle for an online smoke run.

### branch_gate_online_smoke_001

- Type: `branch_selection`
- Decision: `step_0002`
- Rationale: Select the lower-validation-MAE branch (0.627837) from the fresh remote frontier.

### program_search_gate_online_smoke_001

- Type: `program_search_escalation`
- Decision: `run_tiny_openevolve_knapsack`
- Rationale: Exercise the program-search escalation gate in the same online smoke trajectory.

### claim_gate_online_smoke_001

- Type: `claim_audit`
- Decision: `claim_online_orchestration_feasible`
- Rationale: The trajectory proves online orchestration feasibility only; superiority remains unproven.
