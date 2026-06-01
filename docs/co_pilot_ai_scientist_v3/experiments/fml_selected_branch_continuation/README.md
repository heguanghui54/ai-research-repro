# FML Selected-Branch Continuation

This experiment continues from the human-gated branch selected in
`../fml_online_branch_gate_drafts/`.

The selected branch was draft step 2 from the live two-draft frontier. The
continuation runner temporarily applied that code snapshot to the official
FML-bench task template, launched a short AI Scientist-v2 run, and restored the
template files afterward.

## Remote Run

- Host: `ubuntu-heshi`
- Repository: `/home/heshi/work/FML-bench`
- Continuation script:
  `/home/heshi/work/co-pilot-ai-scientist-v3/run_fmlbench_snapshot_continuation.py`
- Local source script:
  `scripts/run_fmlbench_snapshot_continuation.py`
- Selected snapshot:
  `docs/co_pilot_ai_scientist_v3/experiments/fml_online_branch_gate_drafts/step_0002_code.json`
- Output directory:
  `/home/heshi/work/copilotv3-selected-branch-continuation`
- Agent: `ai_scientist_v2`
- Task: `Causality_causalml`
- Provider/model: `DeepSeek` / `deepseek-chat`
- Continuation budget: `2` steps
- Continuation temporary config: `num_ideas=1`, `num_parallel=1`,
  `stage_budgets=[1.0, 0.0, 0.0, 0.0]`

## Results

FML-bench reports lower MAE as better.

| Run segment | Validation MAE | Test MAE | Notes |
| --- | ---: | ---: | --- |
| Baseline | 1.2962585694753708 | N/A | FML-bench baseline validation metric |
| Live two-draft gate selected branch | 0.6212624733836205 | 0.6404510911628365 | Gate selected draft step 2 |
| Selected-branch continuation | 0.4012397173613497 | 0.4021701846791075 | Continued from selected snapshot |

The continuation run produced two validation steps:

| Continuation step | Action | Validation MAE |
| --- | --- | ---: |
| 1 | draft | 1.632096007062123 |
| 2 | improve | 0.4012397173613497 |

## Interpretation

This is the first executable selected-branch continuation evidence for the
Co-Pilot AI Scientist v3 design. It shows that a human gate can choose a branch,
materialize that branch's code snapshot, and allocate additional AI
Scientist-v2 search budget from the selected state.

The comparison is still preliminary. The continuation is implemented by
snapshot seeding rather than by preserving the original in-memory tree object,
and it should be repeated with more seeds and a matched autonomous baseline
before making strong superiority claims.

## Artifacts

- `summary.json`
- `config_used.yaml`
- `step_0001_code.json`
- `step_0002_code.json`
