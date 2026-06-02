# Online Full-Gate Smoke Trajectory

- Trajectory ID: `online_full_gate_smoke_20260602_012208`
- Generated at: `2026-06-02T01:22:08Z`
- Remote host: `ubuntu-heshi`
- Remote root: `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_012208`
- Single online smoke run: `True`

This is a fresh online smoke trajectory that exercises all five gate types and launches remote FML-bench plus OpenEvolve work. It proves orchestration feasibility, not general performance superiority.

## Summary

| Metric | Value |
| --- | ---: |
| `selected_research_direction` | `hitl-gated-tree-search` |
| `selected_branch` | `step_0001` |
| `selected_branch_val_mae` | 0.675172 |
| `continuation_test_mae` | 0.646224 |
| `program_search_best_score` | 0.995619 |
| `same_run_autonomous_enabled` | `True` |
| `same_run_autonomous_steps` | `2` |
| `same_run_autonomous_test_mae` | 0.646224 |
| `branch_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_012208/branch_frontier/ai_scientist_v2/Causality_causalml/20260602_092212_a12964aa/summary.json` |
| `continuation_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_012208/selected_continuation/ai_scientist_v2/Causality_causalml/20260602_092240_890a79f1/summary.json` |
| `program_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_012208/program_search/knapsack_openevolve_1iter/summary.json` |
| `autonomous_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_012208/autonomous_baseline/ai_scientist_v2/Causality_causalml/20260602_092320_a4298743/summary.json` |

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
- Decision: `step_0001`
- Rationale: Select the lower-validation-MAE branch (0.675172) from the fresh remote frontier.

### program_search_gate_online_smoke_001

- Type: `program_search_escalation`
- Decision: `run_tiny_openevolve_knapsack`
- Rationale: Exercise the program-search escalation gate in the same online smoke trajectory.

### claim_gate_online_smoke_001

- Type: `claim_audit`
- Decision: `claim_online_orchestration_feasible`
- Rationale: The trajectory proves online orchestration feasibility only; superiority remains unproven.
