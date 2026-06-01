# Scientific Taste/Insight Coverage Audit

This audit checks whether human gate logs contain enough structured
information to evaluate scientific taste and insight as a logged search
prior. Missing values are reported as missing rather than estimated.

## Summary

- Gate records audited: 18
- Standalone gate log files audited: 8
- Trajectory files audited: 2
- Logs containing any taste/insight object: 1
- Logs with complete taste/insight records: 1
- Logs missing one or more required taste/insight fields: 17
- Mean taste/insight score among complete records: 4.600

## Required Rubric Dimensions

`problem_depth`, `novelty_potential`, `mechanistic_value`, `failure_informativeness`, `benchmark_taste`, `claim_significance`, `risk_asymmetry`

## Per-Gate Coverage

| Gate | Source | Type | Has taste record | Complete | Missing fields |
| --- | --- | --- | --- | --- | --- |
| `branch_gate_causality_after_two_drafts` | `human_gate_log` | `branch_selection` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `branch_gate_causality_online_two_drafts` | `human_gate_log` | `branch_selection` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `branch_gate_fairness_after_two_attempts` | `human_gate_log` | `branch_selection` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `claim_gate_001` | `human_gate_log` | `claim_audit` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `evaluator_gate_fairness_metric_guardrail` | `human_gate_log` | `evaluator_approval` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `idea_gate_001` | `human_gate_log` | `idea_selection` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `program_search_gate_001` | `human_gate_log` | `program_search_escalation` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `scientific_taste_prior_benchmark_portfolio_001` | `human_gate_log` | `scientific_taste_prior` | yes | yes | - |
| `idea_gate_executable_trace_001` | `trajectory_gate[0]` | `idea_selection` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `evaluator_gate_executable_trace_001` | `trajectory_gate[1]` | `evaluator_approval` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `branch_gate_executable_trace_001` | `trajectory_gate[2]` | `branch_selection` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `program_search_gate_executable_trace_001` | `trajectory_gate[3]` | `program_search_escalation` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `claim_gate_executable_trace_001` | `trajectory_gate[4]` | `claim_audit` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `idea_gate_online_smoke_001` | `trajectory_gate[0]` | `idea_selection` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `evaluator_gate_online_smoke_001` | `trajectory_gate[1]` | `evaluator_approval` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `branch_gate_online_smoke_001` | `trajectory_gate[2]` | `branch_selection` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `program_search_gate_online_smoke_001` | `trajectory_gate[3]` | `program_search_escalation` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |
| `claim_gate_online_smoke_001` | `trajectory_gate[4]` | `claim_audit` | no | no | rubric_version, scores, taste_insight_score, qualitative_rationale, non_metric_factors, scores.problem_depth, scores.novelty_potential, scores.mechanistic_value, scores.failure_informativeness, scores.benchmark_taste, scores.claim_significance, scores.risk_asymmetry |

## Interpretation

The package now defines a rubric for logging human scientific taste and
insight. Complete records show where taste was logged prospectively or
as an explicit author decision; incomplete records show older gates or
gates where the field was not captured. Coverage alone does not support
a claim that taste-gated search improves the upper tail of research
outcomes.

Future prospective matched-budget runs must fill `taste_insight` at each
human gate and compare downstream trajectories against autonomous
baselines. This audit is therefore a measurement-readiness artifact, not a
performance result.
