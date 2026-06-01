# Max-Cut Heuristic Search Task

This controlled non-FML benchmark tests the AlphaEvolve/OpenEvolve-style claim
that evolutionary program search can be useful on machine-gradeable algorithmic
subproblems.

The public API is:

```python
def partition_graph(num_nodes, edges, seed=0):
    """Return one side of a graph cut as node indices or 0/1 assignments."""
```

The evaluator generates deterministic weighted graphs with community structure,
scores the returned cut, verifies validity, and normalizes performance against a
deterministic multi-start local-search reference. This is not an official
benchmark score; it is a credential-free, reproducible control task for the
program-search escalation gate.
