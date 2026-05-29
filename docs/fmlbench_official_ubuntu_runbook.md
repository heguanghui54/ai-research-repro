# FML-bench official-repo Ubuntu runbook

This runbook documents the path I actually verified on the SSH-controlled
Ubuntu host for the official
[qrzou/FML-bench](https://github.com/qrzou/FML-bench) repository.

## What was verified

The following end-to-end smoke test was run successfully on Ubuntu:

- official FML-bench repo: `qrzou/FML-bench`
- provider: `DeepSeek`
- model: `deepseek-chat`
- task: `Causality_causalml`
- step budget: `4`
- result: the official benchmark completed and produced validation and test
  scores

The final run reported:

- **Best Val Metric**: `0.5989426968010781`
- **Test Metric**: `0.6177188971481032`
- **Total Steps**: `4`

The summary artifact was written on the Ubuntu host under:

- `/home/heshi/work/fmlbench-smoke-results-fixed2/ai_scientist_v2/Causality_causalml/20260530_004241_dced73c8/summary.json`

## Recommended order

Prefer providers in this order:

1. **DeepSeek**
2. **Monica**

DeepSeek is the cheapest path for this benchmark workflow. Monica is the
fallback when a DeepSeek key is unavailable.

## Ubuntu setup

These commands are meant to be run on the Ubuntu host via SSH.

### 1. Clone the official repo

```bash
git clone https://github.com/qrzou/FML-bench.git
cd FML-bench
```

### 2. Create the benchmark environment

For a minimal first pass, set up only the Causality task:

```bash
python setup.py --task Causality_causalml
```

If you want the full official setup instead, run:

```bash
python setup.py
```

### 3. Configure the LLM provider

Use DeepSeek first:

```bash
export DEEPSEEK_API_KEY="your_deepseek_key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export CUDA_VISIBLE_DEVICES=0
```

If you need Monica instead, the official repo needs a small provider patch.
The helper in this worktree applies it for you:

```bash
python /path/to/ai-research-repro/scripts/patch_fmlbench_monica_provider.py \
  --repo /path/to/FML-bench
export MONICA_API_KEY="your_monica_key"
export MONICA_BASE_URL="https://openapi.monica.im/v1"
```

## 4. Run the smoke test

The helper script in this repository runs the official benchmark entrypoint
with a small step budget.

From anywhere on the Ubuntu host:

```bash
bash /path/to/ai-research-repro/scripts/fmlbench_smoke_test.sh
```

Or, if you are running it from this worktree, point it at the official repo:

```bash
FMLBENCH_REPO_DIR=/path/to/FML-bench \
FMLBENCH_PROVIDER=DeepSeek \
FMLBENCH_MODEL=deepseek-chat \
FMLBENCH_MAX_STEPS=4 \
  /path/to/ai-research-repro/scripts/fmlbench_smoke_test.sh
```

The helper defaults to:

- `configs/agents/ai_scientist_v2.yaml`
- `configs/tasks/causality_causalml.yaml`
- `agent.ai_scientist_v2.max_steps=20`

For the verified smoke test, I used `agent.ai_scientist_v2.max_steps=4`.

## 5. What the benchmark should emit

The official benchmark writes:

- `summary.json`
- `config_used.yaml`
- per-run execution records and code backups

If the run succeeds, you should see a final summary with both validation and
test metrics, not just an initialization log.

## Notes from the verified run

- The official benchmark can be used with `DeepSeek` directly after adding a
  small provider branch in `agents/llm.py`.
- The smoke test is a good first sanity check before trying the full paper
  scale run.
- If the official task workspace is missing, the benchmark will fail while
  backing up or validating files; make sure the task repo exists under
  `workspace/Causality_causalml/causalml` after `setup.py --task
  Causality_causalml`.

## Helper scripts in this worktree

- `scripts/fmlbench_smoke_test.sh`
- `scripts/patch_fmlbench_deepseek_provider.py`
- `scripts/patch_fmlbench_monica_provider.py`
- `scripts/bootstrap_causalml_smoke_repo.py`
