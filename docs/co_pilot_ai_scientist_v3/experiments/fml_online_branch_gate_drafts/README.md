# FML Online Branch-Gate Draft Probe

This experiment is a live AI Scientist-v2/FML-bench run on the SSH Ubuntu host,
not a retrospective replay. It was designed to create a real branch-selection
frontier before a human gate.

## Remote Run

- Host: `ubuntu-heshi`
- Repository: `/home/heshi/work/FML-bench`
- Output directory:
  `/home/heshi/work/copilotv3-online-branch-gate-drafts-fixed`
- Agent: `ai_scientist_v2`
- Task: `Causality_causalml`
- Provider/model: `DeepSeek` / `deepseek-chat`
- Step budget: `2`
- Temporary agent config: `/tmp/ai_scientist_v2_basic2.yaml`
- Stage budget override in temp config: `[1.0, 0.0, 0.0, 0.0]`
- Purpose: force two first-stage draft branches so a branch gate can choose
  which branch deserves further budget.

## Results

FML-bench reports lower MAE as better.

| Candidate | Action | Validation MAE |
| --- | --- | --- |
| step 1 | draft | 1.1496098661684393 |
| step 2 | draft | 0.6212624733836205 |

The benchmark's automatic final test on the best validation branch reported:

- baseline validation MAE: `1.2962585694753708`
- best validation MAE: `0.6212624733836205`
- test MAE: `0.6404510911628365`
- total steps: `2`
- total ideas: `2`
- total tokens: `5868`

## Gate Interpretation

An online `branch_selection` gate after this two-draft frontier would select
step 2 and prune step 1. This is still a small gate probe rather than a complete
resume-enabled human-gated AI Scientist-v2 run, but it is stronger evidence
than retrospective replay because the frontier was generated live specifically
for a gate decision.

## Artifacts

- `summary.json`
- `config_used.yaml`
- `step_0001_code.json`
- `step_0002_code.json`
- `../../human_gate_logs/branch_gate_causality_online_two_drafts.json`
