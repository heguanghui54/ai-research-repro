# FML Matched-Budget Replicate 2: Gated Draft Frontier

This run creates the two-draft branch frontier for the second matched-budget
replicate on `Causality_causalml`.

## Setup

- Remote output root:
  `/home/heshi/work/copilotv3-matched-rep2-gated-drafts`
- FML-bench run id:
  `20260601_210246_9238e9c4`
- Model/provider: `deepseek-chat` through `DeepSeek`
- Steps: 2
- Ideas / parallel branches: 2 / 2
- Stage budgets: `[1.0, 0.0, 0.0, 0.0]`
- Metric: IHDP MAE, lower is better

## Result

The two draft branches produced:

| Step | Validation MAE | Notes |
| ---: | ---: | --- |
| 1 | 4.835164 | Weak branch. |
| 2 | 0.605881 | Selected branch for continuation. |

The automatic final test on the selected draft frontier reported test MAE
`0.646223724015837`.

## Artifacts

- `summary.json`
- `config_used.yaml`
- `step_0001_code.json`
- `step_0002_code.json`
