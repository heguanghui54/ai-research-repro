# Online Full-Gate Smoke Trajectory

- Trajectory ID: `online_full_gate_smoke_20260602_013612`
- Generated at: `2026-06-02T01:36:12Z`
- Remote host: `ubuntu-heshi`
- Remote root: `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502`
- Single online smoke run: `True`

This is a fresh online smoke trajectory that exercises all five gate types and launches remote FML-bench plus OpenEvolve work. It proves orchestration feasibility, not general performance superiority.

## Summary

| Metric | Value |
| --- | ---: |
| `selected_research_direction` | `hitl-gated-tree-search` |
| `task_config` | `configs/tasks/fairness_fairlearn.yaml` |
| `benchmark_name` | `Fairness_fairlearn` |
| `metric_name` | `primary_metric` |
| `selected_branch` | `abort_no_valid_branch` |
| `selected_branch_val_mae` | `None` |
| `selected_branch_val_metric` | `None` |
| `no_valid_branch` | `True` |
| `continuation_test_mae` | `None` |
| `program_search_best_score` | 0.994177 |
| `same_run_autonomous_enabled` | `True` |
| `same_run_autonomous_steps` | `1` |
| `same_run_autonomous_test_mae` | `None` |
| `branch_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502/branch_frontier/ai_scientist_v2/Fairness_fairlearn/20260602_093507_8b36a1f7/summary.json` |
| `continuation_summary_remote` | `None` |
| `program_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502/program_search/knapsack_openevolve_1iter/summary.json` |
| `autonomous_summary_remote` | `/home/heshi/work/copilotv3-online-full-gate-smoke-20260602_013502/autonomous_baseline/ai_scientist_v2/Fairness_fairlearn/20260602_093627_84f7b730/summary.json` |

## Gate Decisions

### idea_gate_online_smoke_001

- Type: `idea_selection`
- Decision: `hitl-gated-tree-search`
- Rationale: Use the currently selected narrow contribution as the online smoke trajectory target.

### evaluator_gate_online_smoke_001

- Type: `evaluator_approval`
- Decision: `fml_metric_plus_guardrails`
- Rationale: Approve a low-cost evaluator bundle for an online smoke run.

### branch_gate_online_smoke_001

- Type: `branch_selection`
- Decision: `abort_no_valid_branch`
- Rationale: No valid branch was available for `configs/tasks/fairness_fairlearn.yaml`; archive this as a failure-mode trajectory.

### program_search_gate_online_smoke_001

- Type: `program_search_escalation`
- Decision: `run_tiny_openevolve_knapsack`
- Rationale: Exercise the program-search escalation gate in the same online smoke trajectory.

### claim_gate_online_smoke_001

- Type: `claim_audit`
- Decision: `claim_online_orchestration_feasible`
- Rationale: The trajectory proves online orchestration feasibility only; superiority remains unproven.
