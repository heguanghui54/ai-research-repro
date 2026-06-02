# MLAgentBench CIFAR10/debug Official Run

This package records the first scored official MLAgentBench `debug` / CIFAR10
run after resolving the earlier slow-download setup blocker.

## Setup Resolution

The official task previously reached
`https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz` but downloaded too
slowly on `ubuntu-heshi`. For this run, the same official CIFAR10 archive was
downloaded on the local machine, copied to:

```text
/home/heshi/work/bench-probes/MLAgentBench/MLAgentBench/benchmarks/cifar10/env/data/cifar-10-python.tar.gz
```

Then the official MLAgentBench prepare command completed:

```bash
cd /home/heshi/work/bench-probes/MLAgentBench
/home/heshi/work/bench-probes/MLAgentBench/.venv/bin/python -u -m MLAgentBench.prepare_task \
  debug /home/heshi/work/bench-probes/MLAgentBench/.venv/bin/python
```

## Baseline

The baseline used the official MLAgentBench runner with `agent-type Agent`,
`max-steps 1`, and `agent-max-steps 1`, which executes the starter `train.py`
and submits `submission.csv`.

- Remote run:
  `/home/heshi/work/copilotv3-mlagentbench-cifar10-debug-official-baseline-20260603`
- Official eval score: `0.5103`
- Official eval total time: `65.81158947944641` seconds

The official `eval.py` initially printed the score but failed to write JSON
because this baseline run did not create the expected top-level `log` file used
by the script's error-classifier helper. After adding an empty `log` file, the
same official eval command wrote `baseline/eval.json`.

## Co-Pilot Selected Branch

The co-pilot selected branch keeps the official dataset and official evaluator
fixed, but replaces the starter training script with a small batch-normalized
CNN, light CIFAR10 augmentation, AdamW, cosine learning-rate decay, label
smoothing, and eight epochs.

- Remote run:
  `/home/heshi/work/copilotv3-mlagentbench-cifar10-debug-human-gated-20260603`
- Official eval score: `0.7782`
- Delta versus baseline: `+0.2679`

## Claim Boundary

This is a scored official MLAgentBench non-FML task and is stronger than the
previous setup-only CIFAR10 probe. It supports benchmark-portfolio expansion
and a concrete co-pilot-selected branch improvement over the starter baseline.
It is still one task and one seed, and it does not prove broad Co-Pilot AI
Scientist v3 superiority or independent human expert validation.
