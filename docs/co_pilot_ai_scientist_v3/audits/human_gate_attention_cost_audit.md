# Human Gate Attention-Cost Audit

This audit checks whether human gate logs contain enough information to measure
human attention cost in matched-budget experiments. Missing values are reported
as missing rather than estimated.

## Summary

- Gate records audited: 18
- Standalone gate log files audited: 8
- Trajectory files audited: 2
- Logs with complete attention-cost records: 0
- Logs missing one or more required attention-cost fields: 18
- Aggregate attention cost: unavailable because no complete gate log has measured minutes.

## Per-Gate Coverage

| Gate | Source | Type | Complete | Missing fields |
| --- | --- | --- | --- | --- |
| `branch_gate_causality_after_two_drafts` | `human_gate_log` | `branch_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `branch_gate_causality_online_two_drafts` | `human_gate_log` | `branch_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `branch_gate_fairness_after_two_attempts` | `human_gate_log` | `branch_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `claim_gate_001` | `human_gate_log` | `claim_audit` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `evaluator_gate_fairness_metric_guardrail` | `human_gate_log` | `evaluator_approval` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `idea_gate_001` | `human_gate_log` | `idea_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `program_search_gate_001` | `human_gate_log` | `program_search_escalation` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `scientific_taste_prior_benchmark_portfolio_001` | `human_gate_log` | `scientific_taste_prior` | no | active_review_minutes, wall_clock_latency_minutes |
| `idea_gate_executable_trace_001` | `trajectory_gate[0]` | `idea_selection` | no | active_review_minutes, wall_clock_latency_minutes |
| `evaluator_gate_executable_trace_001` | `trajectory_gate[1]` | `evaluator_approval` | no | active_review_minutes, wall_clock_latency_minutes |
| `branch_gate_executable_trace_001` | `trajectory_gate[2]` | `branch_selection` | no | active_review_minutes, wall_clock_latency_minutes |
| `program_search_gate_executable_trace_001` | `trajectory_gate[3]` | `program_search_escalation` | no | active_review_minutes, wall_clock_latency_minutes |
| `claim_gate_executable_trace_001` | `trajectory_gate[4]` | `claim_audit` | no | active_review_minutes, wall_clock_latency_minutes |
| `idea_gate_online_smoke_001` | `trajectory_gate[0]` | `idea_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `evaluator_gate_online_smoke_001` | `trajectory_gate[1]` | `evaluator_approval` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `branch_gate_online_smoke_001` | `trajectory_gate[2]` | `branch_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `program_search_gate_online_smoke_001` | `trajectory_gate[3]` | `program_search_escalation` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `claim_gate_online_smoke_001` | `trajectory_gate[4]` | `claim_audit` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |

## Interpretation

The current retrospective and smoke-run gate logs support auditable decision
provenance, but they do not yet support the paper's attention-efficiency
claim. Future prospective matched-budget runs must fill `attention_cost`
for every human gate, including active review minutes, wall-clock latency,
options reviewed, artifacts reviewed, and decision count.

This is a negative measurement-readiness result, not a performance result.
