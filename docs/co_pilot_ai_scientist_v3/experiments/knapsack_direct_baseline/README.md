# Knapsack Direct LLM-Edit Baseline

## Purpose

Compare OpenEvolve-style programmatic search against a one-shot direct LLM
rewrite on a richer knapsack heuristic subproblem.

## Setup

- Host: `ubuntu-heshi`
- Provider: DeepSeek through OpenAI-compatible API
- Model: `deepseek-chat`
- Initial program: `knapsack_task/initial_program.py`
- Evaluator: `knapsack_task/evaluator.py`

## Result

- Direct LLM-edit score: `0.9952700988954383`
- Average optimality ratio: `0.9952700988954383`
- Total value: `17415`
- Total optimum: `17484`
- Invalid instances: `0`

## Interpretation

Direct editing improved the greedy baseline, but left a larger gap than the
five-iteration OpenEvolve run.

