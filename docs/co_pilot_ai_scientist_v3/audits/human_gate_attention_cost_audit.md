# Human Gate Attention-Cost Audit

This audit checks whether human gate logs contain enough information to measure
human attention cost in matched-budget experiments. Missing values are reported
as missing rather than estimated.

## Summary

- Gate logs audited: 7
- Logs with complete attention-cost records: 0
- Logs missing one or more required attention-cost fields: 7
- Aggregate attention cost: unavailable because no complete gate log has measured minutes.

## Per-Gate Coverage

| Gate | Type | Complete | Missing fields |
| --- | --- | --- | --- |
| `branch_gate_causality_after_two_drafts` | `branch_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `branch_gate_causality_online_two_drafts` | `branch_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `branch_gate_fairness_after_two_attempts` | `branch_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `claim_gate_001` | `claim_audit` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `evaluator_gate_fairness_metric_guardrail` | `evaluator_approval` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `idea_gate_001` | `idea_selection` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |
| `program_search_gate_001` | `program_search_escalation` | no | active_review_minutes, wall_clock_latency_minutes, options_reviewed, artifacts_reviewed_count, decision_count |

## Interpretation

The current retrospective and smoke-run gate logs support auditable decision
provenance, but they do not yet support the paper's attention-efficiency
claim. Future prospective matched-budget runs must fill `attention_cost`
for every human gate, including active review minutes, wall-clock latency,
options reviewed, artifacts reviewed, and decision count.

This is a negative measurement-readiness result, not a performance result.
