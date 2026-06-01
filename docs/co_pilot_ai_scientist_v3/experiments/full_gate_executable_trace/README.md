# Executable Full-Gate Trajectory

- Trajectory ID: `copilot_v3_executable_full_gate_trace_001`
- Generated at: `2026-06-01T15:47:16Z`
- Mode: `executable_artifact_replay`
- Single online training run: `False`

This is one continuous executable traversal over archived experiment artifacts. It verifies gate logic and evidence linkage, but it is not a fresh online run of all four loops.

## Gate Decisions

### idea_gate_executable_trace_001

- Type: `idea_selection`
- Decision: `hitl-gated-tree-search`
- Rationale: Select the narrow human-gated tree-search contribution because it is the most experimentally defensible core and can absorb Co-Scientist and OpenEvolve modules as supporting layers.
- Affected artifacts:
  - `docs/co_pilot_ai_scientist_v3/candidates.json`

### evaluator_gate_executable_trace_001

- Type: `evaluator_approval`
- Decision: `correctness_and_utility_guardrails`
- Rationale: The current artifact set contains both invalid fast code and fairness metric-gaming examples, so the evaluator gate must approve guardrails before additional search budget is spent.
- Affected artifacts:
  - `docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_multiseed_summary.json`
  - `docs/co_pilot_ai_scientist_v3/experiments/fml_fairness_evaluator_gate_repair_summary.json`

### branch_gate_executable_trace_001

- Type: `branch_selection`
- Decision: `step_0002`
- Rationale: Select the lower-validation-MAE branch from the live Causality frontier (0.621262).
- Affected artifacts:
  - `docs/co_pilot_ai_scientist_v3/experiments/fml_online_branch_gate_drafts/summary.json`
  - `docs/co_pilot_ai_scientist_v3/experiments/fml_selected_branch_continuation/summary.json`

### program_search_gate_executable_trace_001

- Type: `program_search_escalation`
- Decision: `selective_openevolve`
- Rationale: Escalate selectively: OpenEvolve is useful for richer or correctness-gated subproblems, while the sklearn tabular result shows direct editing can match it on standard small modeling changes.
- Affected artifacts:
  - `docs/co_pilot_ai_scientist_v3/experiments/knapsack_program_search_comparison.md`
  - `docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_comparison.md`
  - `docs/co_pilot_ai_scientist_v3/experiments/sklearn_diabetes_tabular_comparison.md`

### claim_gate_executable_trace_001

- Type: `claim_audit`
- Decision: `claim_feasibility_and_boundary_conditions`
- Rationale: The selected continuation beats the first matched autonomous baseline by 0.019303 MAE in this pair, but the full evidence set is still mixed. The paper should claim an executable co-pilot architecture and logged boundary conditions, not general superiority.
- Affected artifacts:
  - `docs/co_pilot_ai_scientist_v3/paper_en.md`
  - `docs/co_pilot_ai_scientist_v3/paper_zh.md`
  - `docs/co_pilot_ai_scientist_v3/audits/claim_evidence_audit.md`

## Summary Metrics

| Metric | Value |
| --- | ---: |
| `selected_research_direction` | `hitl-gated-tree-search` |
| `selected_branch` | `step_0002` |
| `selected_branch_val_mae` | 0.621262 |
| `selected_continuation_test_mae` | 0.402170 |
| `matched_autonomous_test_mae` | 0.421474 |
| `pair1_test_mae_delta_autonomous_minus_gated` | 0.019303 |
| `knapsack_direct_score` | 0.995270 |
| `knapsack_openevolve_score` | 0.999439 |
| `mlagentbench_vectorization_median_speedup` | 132.672548 |
| `sklearn_direct_rmse` | 55.895460 |
| `sklearn_openevolve_median_rmse` | 55.895460 |

## Remaining Gap

A true online full-gate experiment must generate ideas, approve evaluators, select branches, run program search, and audit claims in one continuous run, then compare against a matched autonomous baseline.
