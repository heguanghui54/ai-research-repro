# Prospective Matched Micro-Pilot: SSH Max-Cut

- Run id: `prospective_matched_micro_pilot_20260603_ssh_maxcut`
- Host: `ubuntu-heshi`
- Status: `pass` under `scripts/audit_prospective_matched_budget_package.py`
- Task: controlled weighted Max-Cut on 12 deterministic 8-node graph
  instances, with brute-force optima used for normalized scoring.

## Matched Conditions

Both conditions used the same generated graph instances, evaluator, tool
access, and deterministic budget. The autonomous baseline used a simple
alternating partition policy. The co-pilot condition used a logged
`frontier_steering` gate to select an inspectable local-search repair policy.

| Condition | Mean normalized score | Minimum normalized score |
| --- | ---: | ---: |
| Autonomous alternating baseline | `0.596214` | `0.290323` |
| Co-pilot selected local search | `0.984419` | `0.904762` |

Mean delta, co-pilot minus autonomous: `+0.388205`.

## Artifacts

- `remote_metrics.json`: full per-instance scores and graph metadata from the
  SSH Ubuntu run.
- `co_pilot_trajectory.json`: co-pilot trajectory with the selected gate.
- `human_gate_logs/frontier_gate_001.json`: complete operator-recorded
  `attention_cost` and `taste_insight` fields.
- `autonomous_baseline_summary.json`: baseline metrics.
- `claim_audit.md`: claim boundary table.
- `manuscript.md`: same-run mini-manuscript artifact.
- `prospective_manifest.json`: package manifest consumed by the prospective
  matched-budget audit.

## Claim Boundary

This run strengthens the evidence shape for Milestone 2 by showing that a
prospective matched co-pilot/autonomous package can be generated on the SSH
Ubuntu host and audited end to end. It does not prove top-conference empirical
sufficiency, paper-quality improvement, or superiority over autonomous AI
Scientist-v2 on real research tasks.
