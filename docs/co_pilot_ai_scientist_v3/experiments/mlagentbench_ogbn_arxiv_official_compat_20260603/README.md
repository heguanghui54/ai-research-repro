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
- Co-pilot-selected full-batch MLP branch official-evaluator scores:
  `0.5399872435857869`, `0.5408925374976853`, and `0.5436289940950148`.
- Three-seed mean score: `0.5415029250594956`.
- Three-seed minimum score: `0.5399872435857869`.
- Three-seed sample standard deviation: `0.0018960528538453166`.
- Mean delta versus compatibility starter: `+0.5140560596396655`.

Claim boundary: this is a scored official MLAgentBench task using the official
OGBN-arxiv evaluator and official prepared data, but the baseline is a
compatibility translation rather than an unmodified original NeighborLoader
starter. It supports non-FML benchmark expansion and dependency-aware task
repair; it does not prove broad benchmark superiority or independent human
scientific-quality improvement.
