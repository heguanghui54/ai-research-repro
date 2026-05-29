# FML-bench Ubuntu reproduction guide

This guide is the practical companion to the paper and the official repository:

- Paper: [arXiv:2605.17373](https://arxiv.org/abs/2605.17373)
- Official repo: [qrzou/FML-bench](https://github.com/qrzou/FML-bench)

The goal here is to reproduce the benchmark workflow on an Ubuntu machine
controlled over SSH, while keeping LLM cost low.

## What to reproduce first

Because the full benchmark is large, the cheapest reliable path is:

1. Set up the official benchmark code
2. Run one task end-to-end
3. Confirm the agent can edit code, run validation, and write results
4. Scale out only if you still want the full paper-level run

That gives you a real reproduction of the benchmark loop without spending
money on the full 18-task sweep immediately.

## Provider choice

For the official repo, prefer `DeepSeek` first.

The upstream code already supports `DeepSeek` as a provider in its LLM layer,
so you can keep the benchmark logic unchanged and only swap the API key and
base URL.

If you want a fallback path for other OpenAI-compatible APIs, this worktree's
minimal scaffold also supports `Monica`.

## Ubuntu setup

Run these on the Ubuntu machine over SSH.

### 1. Clone the official repo

```bash
git clone https://github.com/qrzou/FML-bench.git
cd FML-bench
```

### 2. Install the benchmark environment

The official repo bootstraps tasks, datasets, and conda environments with:

```bash
python setup.py
```

For a smaller and cheaper setup, install only one task first:

```bash
python setup.py --task Causality_causalml
```

### 3. Configure DeepSeek

```bash
export DEEPSEEK_API_KEY="your_deepseek_key"
export CUDA_VISIBLE_DEVICES=0
```

The DeepSeek docs state the OpenAI-compatible base URL is:

```bash
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
```

The official benchmark's LLM layer already knows how to create a DeepSeek
client, so in practice you usually only need the key plus the provider choice.

### 4. Run a cheap smoke test

This is the smallest meaningful reproduction step:

```bash
./scripts/fmlbench_smoke_test.sh
```

If you want to set everything explicitly instead of using the helper script:

```bash
python run_agent_benchmark.py \
  --agent-config configs/agents/ai_scientist_v2.yaml \
  --task-config configs/tasks/causality_causalml.yaml \
  --model deepseek-v4-flash \
  --provider DeepSeek \
  --output-dir results \
  agent.ai_scientist_v2.max_steps=20
```

Why this is the right first run:

- one real benchmark task
- one official agent configuration
- a low step budget
- validation and result capture still happen through the official harness

### 5. Inspect results

The benchmark writes a summary under the output directory. Check:

- `results/.../summary.json`
- `results/.../config_used.yaml`
- the task workspace and run artifacts

## Full paper-style run

If the smoke test succeeds and you want something closer to the paper:

1. Increase `agent.ai_scientist_v2.max_steps` toward `100`
2. Run more than one task config
3. Repeat across multiple rounds if you want stronger comparisons

That will move you closer to the paper's evaluation setup, but it will also
cost more time and API usage.

## What this worktree adds

This worktree does not replace the official benchmark.

It adds:

- a low-cost local scaffold for the idea -> edit -> run -> review loop
- a provider priority of `DeepSeek -> Monica -> OpenAI`
- a minimal reproduction README for quick iteration
- a practical Ubuntu guide for the official benchmark

That makes it easier to validate the workflow cheaply before paying the
full benchmark cost.
