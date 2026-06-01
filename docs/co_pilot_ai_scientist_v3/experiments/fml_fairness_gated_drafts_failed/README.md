# FML-Bench Fairness Gated Drafts Failed Probe

This probe attempted to extend the matched-budget human-gate evidence beyond
the existing Causality pairs by running the FML-Bench `Fairness_fairlearn` task.

Command shape on `ubuntu-heshi`:

```bash
cd /home/heshi/work/FML-bench
export PATH=/home/heshi/miniconda3/bin:/home/heshi/miniconda3/condabin:$PATH
source ~/.codex/env
/home/heshi/work/co-pilot-ai-scientist-v3/.venv/bin/python run_agent_benchmark.py \
  --agent-config configs/agents/ai_scientist_v2.yaml \
  --task-config configs/tasks/fairness_fairlearn.yaml \
  --model deepseek-chat \
  --provider DeepSeek \
  --output-dir /home/heshi/work/copilotv3-fairness-gated-drafts \
  agent.ai_scientist_v2.max_steps=2 \
  agent.ai_scientist_v2.num_ideas=2 \
  agent.ai_scientist_v2.num_parallel=2
```

Outcome:

- Benchmark: `Fairness_fairlearn`
- Metric: `abs_demographic_parity_diff_mean`, lower is better
- Baseline metric: `0.18663158848996153`
- Total attempted steps: `2`
- Successful validation runs: `0`
- Test result: none

Both candidate drafts failed the validation command:

- Run 0 failed because the generated Fairlearn reduction wrapped a sklearn
  pipeline that did not accept `sample_weight`.
- Run 1 failed because `CorrelationRemover` received an invalid
  `sensitive_feature_ids` configuration.

This probe is therefore not counted as matched-budget performance evidence. It
is archived as a failure-mode and evaluator-gate artifact: in cross-task FML
runs, the gate must first require executable validation before any branch is
eligible for continuation.
