# OpenEvolve Smoke Experiment

## Purpose

Verify that the Co-Pilot AI Scientist v3 programmatic-search module can run on
the SSH-controlled Ubuntu host using an open-source AlphaEvolve-style substrate.

## Remote Environment

- Host: `ubuntu-heshi`
- Remote path: `/home/heshi/work/co-pilot-ai-scientist-v3`
- Python: 3.10.12
- OpenEvolve: `0.2.27`
- Provider: DeepSeek through OpenAI-compatible API
- Model: `deepseek-chat`
- API secret handling: keys were sourced from `~/.codex/env`; no keys were
  printed or copied into artifacts.

## Task

The task is a deterministic function-minimization smoke test. The initial
program performs random search over a scalar interval. The evaluator calls
`minimize_function(func, bounds, max_evals=80)` and scores the candidate as the
negative objective value.

This is not a paper-level benchmark. It is a plumbing and feasibility check for:

- OpenEvolve installation on Ubuntu;
- model routing through an OpenAI-compatible endpoint;
- evaluator loading;
- MAP-Elites/island-style OpenEvolve execution;
- artifact capture for later paper writing.

## Result

The run completed one OpenEvolve iteration.

- Initial program score: `0.0345`
- Best evolved score: `0.03781575382850673`
- Improvement: approximately `+0.0033`
- Best program ID: `a637a2cf-d272-438a-9a16-3ec0975a5493`
- Best `x`: `1.3103418307566266`
- Best objective value: `-0.03781575382850673`

OpenEvolve replaced the random-search baseline with a simulated-annealing-style
local search with adaptive step-size shrinkage and occasional random restarts.

## Artifacts

- `summary.json`: run-level summary.
- `openevolve.log`: full OpenEvolve execution log.
- `initial_program.py`: baseline program.
- `evaluator.py`: evaluator used by OpenEvolve.
- `best_program.py`: evolved program.
- `best_program_info.json`: OpenEvolve best-program metadata.

## Interpretation

This run proves that the programmatic-search module is operational on the remote
Ubuntu machine. It does not yet prove the paper's main claim that human-gated
co-pilot research produces better papers. The next required step is to compare
OpenEvolve against a direct LLM-edit baseline and to run a human-gated research
task variant.

That direct baseline has now been run. On this one-iteration smoke task, the
direct LLM edit slightly outperformed OpenEvolve. See
`../program_search_comparison.md`.
