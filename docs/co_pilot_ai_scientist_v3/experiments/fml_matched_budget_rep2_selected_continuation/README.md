# FML Matched-Budget Replicate 2: Selected-Branch Continuation

This run continues from the second replicate's selected draft snapshot.

## Setup

- Remote output root:
  `/home/heshi/work/copilotv3-matched-rep2-selected-continuation`
- FML-bench run id:
  `20260601_210407_dbdea976`
- Model/provider: `deepseek-chat` through `DeepSeek`
- Continuation steps: 2
- Ideas / parallel branches: 1 / 1
- Stage budgets: `[1.0, 0.0, 0.0, 0.0]`
- Metric: IHDP MAE, lower is better

The selected draft snapshot came from
`fml_matched_budget_rep2_gated_drafts/step_0002_code.json`.

## Result

The continuation reached best validation MAE `0.627836868090553` and test MAE
`0.6462237240158367`. This is effectively unchanged from the selected
two-draft frontier test score, so this replicate is a neutral/negative
continuation result for the human-gated path.

## Artifacts

- `summary.json`
- `config_used.yaml`
- `step_0001_code.json`
- `step_0002_code.json`
