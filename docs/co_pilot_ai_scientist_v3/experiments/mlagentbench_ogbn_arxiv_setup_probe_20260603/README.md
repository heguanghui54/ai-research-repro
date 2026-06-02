# MLAgentBench OGBN-arxiv Setup Probe

This probe tests whether MLAgentBench `ogbn-arxiv` can become the next official
non-FML benchmark after CIFAR10/debug.

Result: the task is closer to runnable than IMDB, CLRS, and house-price. The
Ubuntu host can download the OGBN-arxiv data from Stanford SNAP, and the
official prepare script completes after setting
`TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1` for PyTorch 2.6+ compatibility. The starter
baseline still does not produce an official score because PyG neighbor sampling
requires `pyg-lib` or `torch-sparse`; no matching wheel was available in the
current torch 2.12 CPU environment, and a source build was stopped after it
became a long compile.

Claim boundary: this is a repaired setup probe and next-task selection signal,
not a scored official MLAgentBench result.
