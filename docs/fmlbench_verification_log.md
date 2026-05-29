# FML-bench verification log

This log records what was verified in this worktree and on the Ubuntu host
reachable via `ssh ubuntu-heshi`.

## Verified in this worktree

- The official FML-bench helper scripts for DeepSeek and Monica were added.
- A dedicated Ubuntu runbook was written for the official repository.
- The repository is pushed to GitHub on branch `codex/fmlbench-minimal`.

## Verified on Ubuntu

### 1. Official FML-bench CLI help path works

Command:

```bash
ssh ubuntu-heshi 'cd ~/work/FML-bench && python3 run_agent_benchmark.py --help'
```

Result:

- `run_agent_benchmark.py` starts successfully
- the CLI exposes `--agent-config`, `--task-config`, `--model`, `--provider`,
  and `--output-dir`

### 2. DeepSeek provider patch works

Command:

```bash
ssh ubuntu-heshi 'cd ~/work/FML-bench && python3 /home/heshi/patch_fmlbench_deepseek_provider.py --repo /home/heshi/work/FML-bench'
```

Result:

- the official repo now accepts `provider=DeepSeek`
- the provider branch uses `DEEPSEEK_API_KEY` and
  `https://api.deepseek.com`

### 3. Monica provider patch works

Command:

```bash
ssh ubuntu-heshi 'cd ~/work/FML-bench && python3 /home/heshi/patch_fmlbench_monica_provider.py --repo /home/heshi/work/FML-bench'
```

Then:

```bash
ssh ubuntu-heshi 'cd ~/work/FML-bench && MONICA_API_KEY=testkey python3 - <<\"PY\"\nfrom agents.llm import create_client\nclient, model = create_client(\"gpt-4o-mini\", \"Monica\")\nprint(model)\nprint(client.base_url)\nPY'
```

Result:

- the official repo now accepts `provider=Monica`
- the constructed client points to `https://openapi.monica.im/v1`

### 4. Official DeepSeek smoke test completed successfully

Command:

```bash
ssh ubuntu-heshi 'cd /home/heshi/work/FML-bench && \
  env DEEPSEEK_API_KEY="sk-..." DEEPSEEK_BASE_URL="https://api.deepseek.com" \
  CUDA_VISIBLE_DEVICES=0 \
  /home/heshi/miniconda3/bin/conda run -n fmlbench python run_agent_benchmark.py \
  --agent-config configs/agents/ai_scientist_v2.yaml \
  --task-config configs/tasks/causality_causalml.yaml \
  --model deepseek-chat \
  --provider DeepSeek \
  --output-dir /home/heshi/work/fmlbench-smoke-results-fixed2 \
  agent.ai_scientist_v2.max_steps=4'
```

Result:

- the official benchmark completed end-to-end
- validation and test metrics were produced
- the final summary reported:
  - Best Val Metric: `0.5989426968010781`
  - Test Metric: `0.6177188971481032`
  - Total Steps: `4`

## What remains unreproduced

The current work proves the official workflow and provider wiring, but not the
full paper-scale 18-task sweep or the paper's reported aggregate numbers.

To reach the full paper setup, you would still need:

- the full task sweep
- enough API budget and compute time
- any additional benchmark-specific repeats or comparison runs

