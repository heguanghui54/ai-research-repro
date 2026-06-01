# Programmatic Search Comparison

## Setup

Both runs used the same remote host, initial program, evaluator, provider, and
model family.

- Host: `ubuntu-heshi`
- Initial program: `openevolve_smoke/initial_program.py`
- Evaluator: `openevolve_smoke/evaluator.py`
- Provider: DeepSeek
- Model: `deepseek-chat`

## Results

| Method | Budget | Score | Best x | Best objective value |
| --- | ---: | ---: | ---: | ---: |
| Initial random-search program | 0 LLM edits | 0.0345 | 1.3568 | -0.0345 |
| OpenEvolve | 1 evolution iteration | 0.0378157538 | 1.3103418308 | -0.0378157538 |
| OpenEvolve | 5 evolution iterations | 0.0380071496 | 1.3171456876 | -0.0380071496 |
| Direct LLM edit | 1 rewrite | 0.0380213971 | 1.3198669341 | -0.0380213971 |

## Finding

The direct LLM edit slightly outperformed both the one-iteration and
five-iteration OpenEvolve runs on this tiny smoke task. The most defensible
interpretation is not that direct editing is generally better, but that the value
of OpenEvolve-style search is budget-, evaluator-, and task-dependent.

## Implication for Co-Pilot AI Scientist v3

The programmatic-search module needs a human or policy gate:

- use direct edits for very small budgets or simple local improvements;
- escalate to OpenEvolve when the evaluator is reliable, the search space is
  rich, and the budget is large enough for population-level search to matter;
- record the escalation decision as a reproducibility artifact.
