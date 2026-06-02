# MLAgentBench CLRS Baseline Smoke Probe

- Date: 2026-06-02
- Remote host: `ubuntu-heshi`
- Remote run root: `/home/heshi/work/copilotv3-mlagentbench-clrs-baseline-smoke-20260602b`
- MLAgentBench commit: `5d71205cc20a8e95d43aa7cb7120e89ca3323e31`
- Task: `CLRS`
- Agent type: `Agent`
- Runner timeout: 900 seconds
- Eval timeout: 300 seconds

## Purpose

This probe tests whether a second official non-FML MLAgentBench task can be
added to the Co-Pilot AI Scientist v3 evidence portfolio. It targets CLRS
because earlier inspection showed that CLRS, IMDB, and vectorization are the
MLAgentBench tasks with evaluation scripts that do not require Kaggle
preparation. Vectorization is already scored in the package; IMDB is blocked by
Hugging Face access from the Ubuntu host; CLRS was therefore the next plausible
official task.

## Setup Progress

The previous dependency blocker was repaired. The correct DeepMind CLRS package
is `dm-clrs`, not the unrelated PyPI package named `CLRS`. The final import
check passed:

- `clrs==2.0.3`
- `jax==0.6.2`
- `tensorflow==2.21.0`
- `absl==2.4.0`
- `haiku==0.0.16`
- `optax==0.2.8`
- `chex==0.1.90`
- `tensorflow_datasets==4.9.9+nightly`

## Runner Outcome

The MLAgentBench runner reached the official CLRS task prompt and launched
`train.py` on the `floyd_warshall` task. The run then timed out after the
900-second runner limit. No `checkpoints/best.pkl` file was produced, and the
subsequent evaluator emitted an empty JSON object. The runner exit code was
`124`, the standard `timeout` exit code.

## Evidence Files

- `env_check.log`: environment and dependency import record.
- `run.log`: runner invocation, CLRS task prompt, and train launch.
- `eval.log`: evaluator invocation log.
- `eval.json`: empty evaluator output (`{}`), confirming no score.
- `runner_exit_code.txt`: `124`.

## Claim Boundary

This is setup and cost evidence, not a scored benchmark result. It improves the
official benchmark audit by showing that CLRS dependencies can be repaired and
that MLAgentBench can enter the CLRS baseline runner, but it does not provide a
second scored official non-FML result. A future scored CLRS run would need
either a longer CPU/GPU budget, a reduced official training configuration with a
pre-registered scoring rule, or a cached checkpoint/evaluation path.

Follow-up note: a reduced feasibility run was attempted with one training step,
length 4, batch size 1, and hidden size 16. It also timed out before checkpoint
creation, so the current package treats CLRS as a CPU-cost blocker rather than
a near-term scored benchmark.
