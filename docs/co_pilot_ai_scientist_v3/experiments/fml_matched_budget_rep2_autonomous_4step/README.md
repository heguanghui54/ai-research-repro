# FML Matched-Budget Replicate 2: Autonomous 4-Step Baseline

This run is the autonomous matched-budget baseline paired with replicate 2 of
the human-gated path.

## Setup

- Remote output root:
  `/home/heshi/work/copilotv3-matched-rep2-autonomous-4step`
- FML-bench run id:
  `20260601_210500_e65de01b`
- Model/provider: `deepseek-chat` through `DeepSeek`
- Steps: 4
- Ideas / parallel branches: 2 / 2
- Stage budgets: `[0.5, 0.5, 0.0, 0.0]`
- Metric: IHDP MAE, lower is better

## Result

The autonomous run reached best validation MAE `0.5379716029896986` at step 3
and test MAE `0.5956850978622356`.

In the second matched replicate, this autonomous baseline outperformed the
snapshot-seeded human-gated continuation on held-out test MAE
(`0.595685` versus `0.646224`). This result is archived as negative evidence
against any broad claim that branch gating reliably improves outcomes.

## Artifacts

- `summary.json`
- `config_used.yaml`
- `step_0001_code.json`
- `step_0002_code.json`
- `step_0003_code.json`
- `step_0004_code.json`
