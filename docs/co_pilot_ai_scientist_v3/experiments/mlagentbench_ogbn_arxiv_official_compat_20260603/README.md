# MLAgentBench OGBN-arxiv Official-Evaluator Compatibility Run

This experiment advances the OGBN-arxiv probe from setup-only evidence to a
scored official-evaluator path. The original MLAgentBench starter uses
`NeighborLoader`, which failed in the current torch 2.12 CPU environment because
PyG neighbor sampling requires `pyg-lib` or `torch-sparse`. Instead of compiling
that backend, this run uses the official prepared OGBN-arxiv data and the
official MLAgentBench `eval.py`, while replacing the starter training loop with
a full-batch MLP compatibility translation that does not require NeighborLoader.

Results:

- Compatibility starter baseline official-evaluator score: `0.02744686541983005`.
- Co-pilot-selected full-batch MLP branch official-evaluator score:
  `0.5399872435857869`.
- Delta: `+0.5125403781659569`.

Claim boundary: this is a scored official MLAgentBench task using the official
OGBN-arxiv evaluator and official prepared data, but the baseline is a
compatibility translation rather than an unmodified original NeighborLoader
starter. It supports non-FML benchmark expansion and dependency-aware task
repair; it does not prove broad benchmark superiority or independent human
scientific-quality improvement.
