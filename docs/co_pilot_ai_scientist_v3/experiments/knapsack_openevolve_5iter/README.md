# Knapsack OpenEvolve Five-Iteration Run

## Purpose

Test whether OpenEvolve-style population search can outperform direct LLM
editing on a richer machine-gradeable subproblem.

## Setup

- Host: `ubuntu-heshi`
- OpenEvolve: `0.2.27`
- Provider: DeepSeek through OpenAI-compatible API
- Model: `deepseek-chat`
- Iterations: 5
- Random seed: 42
- Initial program: `knapsack_task/initial_program.py`
- Evaluator: `knapsack_task/evaluator.py`

## Result

- Initial greedy score: `0.9915186650509469`
- Direct LLM-edit score: `0.9952700988954383`
- OpenEvolve 5-iteration score: `0.9994394752555711`
- Total value: `17474`
- Total optimum: `17484`
- Invalid instances: `0`
- Best program ID: `afc6104d-1a02-4c90-87e7-a159cb3b5ec1`

## Interpretation

Unlike the scalar function-minimization smoke task, this richer heuristic-search
task shows a clear benefit from OpenEvolve-style search. The evolved program
adds local improvement through one-item and two-item removal followed by greedy
refill, closing most of the gap to the exact dynamic-programming optimum.

This is the first positive evidence for the Co-Pilot AI Scientist v3
`program_search_gate`: direct editing can be enough for small local rewrites,
but a more structured machine-gradeable subproblem can justify escalation to
population search.

