# Knapsack Heuristic Search Task

## Purpose

Create a richer machine-gradeable subproblem than scalar function minimization
to test when OpenEvolve-style programmatic search is worth escalating to.

## Task

Implement:

```python
def select_items(items, capacity):
    ...
```

The function returns item indices for 0/1 knapsack instances. Items are
dictionaries with `weight`, `value`, and `category` keys. The evaluator compares
the selected value against an exact dynamic-programming optimum over 18
deterministic instances.

## Baseline

The initial program uses value/weight greedy selection.

- Initial score: `0.9915186650509469`
- Total value: `17337`
- Total optimum: `17484`
- Invalid instances: `0`

