# ScienceAgentBench Setup Probe

This probe records the current status of ScienceAgentBench on the SSH Ubuntu
host. It is not counted as a completed benchmark run.

## Observed State

- Repository path: `/home/heshi/work/bench-probes/ScienceAgentBench`
- Repository commit: `72220ee`
- Code is present, including `run_infer.py`, `run_eval.py`, and the dockerized
  evaluation harness under `evaluation/harness/`.
- The local `benchmark/` directory only contains a placeholder README.
- Full benchmark artifacts such as `datasets/`, `eval_programs/`,
  `gold_programs/`, and `scoring_rubrics/` are not present.

## Interpretation

ScienceAgentBench is a good next benchmark for evaluator and claim-gate
experiments because it evaluates data-driven scientific discovery programs
extracted from publications. However, the official README says the full
benchmark artifacts must be downloaded separately and should not be
redistributed after unzipping. Because the full benchmark data are absent on the
current Ubuntu host, this turn does not report ScienceAgentBench scores.

## Next Action

Before using ScienceAgentBench as evidence in the paper:

1. Download the verified benchmark artifacts on the Ubuntu host.
2. Keep the unzipped benchmark data out of this GitHub repository.
3. Run one small instance through the official harness or direct evaluator.
4. Archive only permissible logs, metrics, instance IDs, and generated code
   summaries in this repository.
