# Max-Cut Program-Search Comparison

This controlled non-FML task evaluates a weighted Max-Cut heuristic over 16
deterministic graph instances. The evaluator checks that the returned partition
is valid and normalizes cut value against a deterministic multi-start
local-search reference.

| Method | Score / avg ratio | Invalid | Total cut | Reference total |
| --- | ---: | ---: | ---: | ---: |
| Alternating starter | 0.734680 | 0 | 8431 | 11621 |
| Direct DeepSeek rewrite | 0.962237 | 0 | 11189 | 11621 |
| OpenEvolve 5 iter, seed 11 | 0.970833 | 0 | 11271 | 11621 |

OpenEvolve improved over the starter by `+0.236153` and over the direct rewrite
by `+0.008596`. This is a small but positive controlled result for the
AlphaEvolve-style subproblem module. Together with knapsack, it supports the
narrow claim that program search can help on richer machine-gradeable
algorithmic subproblems.

The result does not prove that OpenEvolve should always replace direct editing:
the direct rewrite is already strong, the margin is small, and this is a single
seed. The correct design implication is still an escalation gate: use
programmatic search when the evaluator is reliable, the search space is rich
enough, and the expected value justifies the API/compute budget.
