# Direct LLM-Edit Baseline

## Purpose

Provide a one-shot baseline for the OpenEvolve smoke experiment using the same
initial program, evaluator, provider, and model family.

## Remote Environment

- Host: `ubuntu-heshi`
- Remote path: `/home/heshi/work/co-pilot-ai-scientist-v3`
- Provider: DeepSeek through OpenAI-compatible API
- Model: `deepseek-chat`
- API secret handling: keys were sourced from `~/.codex/env`; no keys were
  printed or copied into artifacts.

## Method

The script `scripts/run_direct_llm_edit_baseline.py` asks the model for one
complete rewrite of `minimize_function(func, bounds, max_evals=80)`, saves the
candidate program, and evaluates it with the same evaluator used by the
OpenEvolve smoke task.

## Result

- Direct LLM-edit score: `0.03802139712357032`
- Best `x`: `1.3198669341118094`
- Best objective value: `-0.03802139712357032`

The one-shot direct edit slightly outperformed the one-iteration OpenEvolve
smoke score of `0.03781575382850673`.

## Interpretation

This is an important boundary result. It does not invalidate OpenEvolve; it
shows that at extremely small budgets, direct LLM editing may be competitive or
better. Co-Pilot AI Scientist v3 should therefore use a structured
`program_search_gate` to decide when to escalate to OpenEvolve-style evolution,
rather than always using it by default.

