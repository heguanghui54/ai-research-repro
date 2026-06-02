# End-to-End Paired Trajectory Audit

- Audit date: `2026-06-02T13:16:09Z`
- Status: `pass_same_run_smoke_pair`
- Evidence level: `same_run_smoke_pair`
- Trajectory: `docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/trajectory.json`
- Co-pilot manuscript: `docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/online_manuscript/co_pilot_online_full_gate_manuscript.md`
- Autonomous manuscript: `docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/online_manuscript/autonomous_online_comparator_manuscript.md`
- Matched continuous trajectory: `True`
- Gate count: `5`
- Metric winner: `autonomous`
- Manuscript internal-score winner: `co_pilot`
- Superiority supported: `False`

## Metrics

- Co-pilot benchmark metric: `0.8620153718142042`
- Autonomous benchmark metric: `0.6404510911628365`
- Lower is better: `True`
- Co-pilot manuscript internal score: `4.64`
- Autonomous manuscript internal score: `3.48`

## Errors

- None

## Claim Boundary

This is a same-run smoke pair from gate orchestration to manuscript production. In this pair the autonomous baseline wins the benchmark metric while the co-pilot manuscript wins the internal manuscript structure/claim-calibration score. It supports workflow completion and comparison readiness, not empirical superiority over autonomous AI Scientist-v2.
