# FML-bench minimal reproduction

This repository is a **low-cost, minimal reproduction scaffold** for the
`FML-bench` paper and GitHub workflow.

What it does:

1. Runs a tiny, deterministic NanoGPT-style benchmark locally
2. Uses the same idea -> edit -> run -> review loop described in the paper
3. Picks an LLM provider in this order: `DeepSeek` -> `Monica` -> `OpenAI`
4. Falls back to deterministic heuristics if no API key is available

What it does not do:

1. It does **not** clone or execute the full 18-task official benchmark
2. It does **not** claim the paper's reported numbers
3. It is meant to keep cost in the "few dollars" range, or zero if you skip APIs

## Why this is the right minimal path

The paper's main idea is the evaluation loop, not a single model trick:

- a baseline codebase
- candidate ideas
- validation runs
- best-run selection
- a short writeup and review

This repo keeps that loop, but shrinks the benchmark to a local toy task so
you can verify the plumbing cheaply before touching the heavy official setup.

## Install

```bash
python -m pip install -r requirements.txt
```

## Minimal run

Use `DeepSeek` first if you have it. If not, the code falls back to `Monica`,
then `OpenAI`.

```bash
export DEEPSEEK_API_KEY="your_key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"

# optional fallback
export MONICA_API_KEY="your_key"
export MONICA_BASE_URL="https://openapi.monica.im/v1"

python -m ai_research_repro.cli run \
  --workspace runs/fmlbench-minimal \
  --ideas 2
```

If you want to force a provider:

```bash
python -m ai_research_repro.cli run \
  --workspace runs/fmlbench-minimal \
  --ideas 2 \
  --provider deepseek
```

If no API keys are set, the pipeline still runs with deterministic fallback
ideas and reviews.

## Outputs

The run writes:

- `runs/fmlbench-minimal/artifacts/baseline_config.json`
- `runs/fmlbench-minimal/artifacts/ideas.json`
- `runs/fmlbench-minimal/artifacts/report.md`
- `runs/fmlbench-minimal/artifacts/review.json`
- `runs/fmlbench-minimal/artifacts/summary.json`
- `runs/fmlbench-minimal/artifacts/best_learning_curve.png`

## How this maps to the paper

The paper compares search strategies over many ML tasks. This scaffold keeps
the same structure but uses one tiny local benchmark so the setup stays cheap:

- `baseline` -> the default NanoGPT-lite config
- `ideas` -> candidate search directions
- `validation` -> repeated local training runs
- `best candidate` -> the best validation loss
- `report` -> a short markdown summary

If you later want the full benchmark, use the official repo:

- [qrzou/FML-bench](https://github.com/qrzou/FML-bench)

For a practical Ubuntu-side runbook that starts with a cheap smoke test and
then scales up, see
[docs/fmlbench_official_ubuntu_runbook.md](docs/fmlbench_official_ubuntu_runbook.md).
中文复现说明见
[docs/fmlbench_中文复现说明.md](docs/fmlbench_中文复现说明.md).
The helper script for the official repo is
[scripts/fmlbench_smoke_test.sh](scripts/fmlbench_smoke_test.sh).
If you need the Monica fallback on the official repo, use
[scripts/patch_fmlbench_monica_provider.py](scripts/patch_fmlbench_monica_provider.py).
If the installed Fairlearn API is older than the generated code expects, use
[scripts/patch_fmlbench_fairlearn_compat.py](scripts/patch_fmlbench_fairlearn_compat.py).
For the actual Ubuntu verification record, see
[docs/fmlbench_verification_log.md](docs/fmlbench_verification_log.md).

On an Ubuntu machine, the official repo still needs task repos, conda envs, and
GPU time, so it is better to validate this minimal scaffold first.

## Repro notes

1. The provider order is cost-aware by default.
2. DeepSeek is preferred because it is usually the cheapest option for this use.
3. Monica is the fallback if DeepSeek is unavailable.
4. The code stays deterministic when no API is configured.
