# FML Autonomous Matched-Budget 4-Step Baseline

This run is a same-task autonomous comparison for the human-gated
selected-branch continuation.

- Remote output root:
  `/home/heshi/work/copilotv3-autonomous-matched-budget-4step`
- Benchmark: `Causality_causalml`
- Model/provider: `deepseek-chat` / `DeepSeek`
- Total AI Scientist-v2 steps: `4`
- Initial ideas: `2`
- Parallel branches: `2`
- Stage budgets: `[0.5, 0.5, 0.0, 0.0]`
- Human gates: none

## Result

- Best validation MAE: `0.38945144308464624`
- Held-out test MAE: `0.42147360723655275`

The corresponding human-gated path reached test MAE `0.4021701846791075` after
two initial draft steps plus two selected-branch continuation steps. This is a
single-task pilot comparison, not a statistical result.
