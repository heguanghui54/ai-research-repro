# MLAgentBench Vectorization Baseline

This is the first non-FML-bench benchmark probe for Co-Pilot AI Scientist v3.
It verifies that MLAgentBench can run on the SSH Ubuntu host and provides a
lightweight task suitable for later branch-gate or program-search experiments.

## Remote Run

- Host: `ubuntu-heshi`
- Repository: `/home/heshi/work/bench-probes/MLAgentBench`
- Commit: `5d71205`
- Task: `vectorization`
- Agent: MLAgentBench `Agent` baseline
- Log directory:
  `/home/heshi/work/copilotv3-mlagentbench-vectorization-baseline`
- Eval output:
  `/home/heshi/work/copilotv3-mlagentbench-vectorization-baseline-eval.json`

## Why This Benchmark

The vectorization task asks an agent to inspect and improve a NumPy convolution
implementation. It is useful for this project because:

- it is not FML-bench;
- it is machine-gradeable by runtime;
- it exposes code snapshots and an action trace;
- it can support a later program-search escalation gate;
- it is much cheaper than Kaggle-style or paper-replication benchmarks.

## Baseline Result

MLAgentBench reports lower runtime as better.

- Final score: `3.17250394821167` seconds
- Total benchmark time: `3.3655309677124023` seconds
- Submitted final answer: `true`
- Error flags: all false

## Setup Notes

The official MLAgentBench package imports several optional agent backends at
startup. To run even the simple baseline in the current environment, the venv
needed targeted dependency installation. The repository-wide `requirements.txt`
attempted to clone `dm-clrs` over the `git://` protocol and timed out on the
Ubuntu host, so this smoke run avoided the full requirements file.

## Artifacts

- `summary.json`
- `eval.json`
- `trace.json`
- `run.log`
- `overall_time.txt`
- `final_train.py`
- `submission.csv`

## Next Experiment

Use the `vectorization` task as a non-FML branch/program-search benchmark:

1. Run a direct LLM rewrite baseline on `train.py`.
2. Run OpenEvolve or another code-evolution loop over the forward function.
3. Add a `program_search_escalation` human gate deciding whether runtime
   optimization deserves deeper search.
