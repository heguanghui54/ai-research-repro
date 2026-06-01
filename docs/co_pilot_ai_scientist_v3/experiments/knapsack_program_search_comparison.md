# Knapsack Programmatic Search Comparison

| Method | Budget | Score | Total value | Total optimum | Invalid |
| --- | ---: | ---: | ---: | ---: | ---: |
| Greedy baseline | 0 LLM edits | 0.9915186651 | 17337 | 17484 | 0 |
| Direct LLM edit | 1 rewrite | 0.9952700989 | 17415 | 17484 | 0 |
| OpenEvolve | 5 iterations | 0.9994394753 | 17474 | 17484 | 0 |

## Finding

On the richer knapsack heuristic task, OpenEvolve outperformed both the initial
greedy baseline and the direct LLM-edit baseline.

## Implication

This supports the Co-Pilot AI Scientist v3 policy that programmatic-search
escalation should depend on task structure:

- scalar/local tasks may not need population search;
- richer combinatorial or heuristic tasks can benefit from OpenEvolve-style
  exploration;
- human or policy gates should decide whether to spend the extra budget.

