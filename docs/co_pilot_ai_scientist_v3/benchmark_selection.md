# Benchmark Selection Strategy

Co-Pilot AI Scientist v3 should not be evaluated only on FML-bench. FML-bench
is useful because it is already runnable in the current Ubuntu environment and
exercises AI Scientist-v2-style branch search, but the paper's claims span more
than one benchmark can measure.

The benchmark suite is therefore selected by claim type.

The companion `benchmark_claim_matrix.md` file records the current mapping from
claims to evidence. It should be updated whenever a new benchmark is added or a
setup probe becomes a scored run.

## Selection Criteria

1. **Matches a paper claim**: the benchmark must measure one part of the
   co-pilot claim, not just generic coding skill.
2. **Execution-grounded**: outputs should be scored by code execution,
   leaderboard-like metrics, or explicit rubrics.
3. **Supports human-gate ablations**: the benchmark should expose decision
   points where idea, evaluator, branch, program-search, or claim gates can be
   inserted.
4. **Runnable under budget**: early evidence should fit the SSH Ubuntu host and
   API budget; high-cost benchmarks can be framed as stretch experiments.
5. **Reproducible artifacts**: the benchmark should produce logs, code
   snapshots, metrics, and enough metadata to support a paper claim.

## Tiered Suite

| Tier | Benchmark | What it tests | Use in this project | Current status |
| --- | --- | --- | --- | --- |
| A | FML-bench | AI Scientist-v2-style ML benchmark search over target code | Branch gate, selected-branch continuation, evaluator failures | Runnable and already used |
| A | OpenEvolve-controlled tasks | Machine-gradeable program search | AlphaEvolve-style escalation gate and direct-edit ablation | Runnable; function minimization, knapsack, and Max-Cut archived |
| B | MLAgentBench | End-to-end ML experimentation agents | Broader ML experiment-loop validation beyond FML-bench | Vectorization task now has an eight-seed controlled probe; CIFAR10/debug is now a scored official run after pre-caching the official CIFAR10 archive, with starter baseline `0.5103` and a three-seed co-pilot-selected mean of `0.7743` (min `0.7709`, std `0.003676`); IMDB dependency was repaired but HuggingFace data access is blocked; CLRS dependencies were repaired and the runner entered `train.py`, but both the official CPU-only baseline and a reduced feasibility run timed out without a checkpoint; house-price reached the official prepare script but is blocked by Kaggle CLI and likely competition-consent requirements |
| B | sklearn diabetes tabular probe | Lightweight supervised-learning model search | Non-FML, non-runtime-only boundary test for direct edit vs program search | Three OpenEvolve seeds and one direct rewrite archived |
| B | ScienceAgentBench | Data-driven scientific discovery code tasks from publications | Non-FML scientific workflow validation, especially evaluator/claim gates | Code present; HuggingFace metadata and verified artifacts currently unreachable from Ubuntu host |
| C | MLE-bench Lite | Kaggle-style ML engineering | High-signal, higher-cost end-to-end ML engineering evidence | Stretch benchmark |
| C | PaperBench | Replication of ML research papers with hierarchical rubrics | Claim/paper-quality and long-horizon research replication evidence | Stretch benchmark |
| C | AIRS-Bench | Full ML research lifecycle tasks | Closest match to full automated research lifecycle if setup fits budget | Stretch benchmark |

## Why FML-bench Remains Useful

FML-bench is the best near-term benchmark for this repository because:

- it has already been set up on `ubuntu-heshi`;
- it uses the AI Scientist-v2 agent directly;
- it yields validation/test metrics and step snapshots;
- it exposes natural branch-gate checkpoints;
- it supports low-budget smoke runs that can be repeated.

However, it should be framed as **one evidence source**, not the full evaluation
of Co-Pilot AI Scientist v3.

## Recommended Next Runs

1. **More matched FML/causal tasks**: keep FML-bench as the branch-gate
   substrate, but extend beyond the current Causality pairs to additional
   tasks, seeds, and budget schedules before making any human-gate superiority
   claim.
2. **Additional controlled program-search probes**: Max-Cut now adds a second
   combinatorial optimization task beyond knapsack. OpenEvolve reaches
   `0.970833` versus direct rewrite `0.962237`, a small single-seed positive
   margin that supports selective escalation rather than automatic program
   search.
3. **Second non-FML controlled modeling probe**: the sklearn diabetes tabular regression
   probe now tests a small supervised-learning modeling subproblem. Both direct
   editing and OpenEvolve improve the rudimentary mean predictor, and direct
   editing matches OpenEvolve, so this acts as a boundary condition for the
   escalation policy.
4. **MLAgentBench vectorization and CIFAR10/debug extension**: baseline, direct LLM rewrite, and
   OpenEvolve-style runtime optimization now run under a correctness-gated
   evaluator with an eight-seed robustness probe. A follow-up official
   CIFAR10/debug setup probe repaired the missing `torchvision` dependency but
   stopped at slow CIFAR10 data download. A 2026-06-02 refresh probe fixed the
   relative-Python invocation, confirmed that the official CIFAR archive is
   reachable from `ubuntu-heshi`, and then terminated after about 61 seconds
   because only about 3.28 MB of the 170 MB archive had downloaded. On
   2026-06-03, the official CIFAR10 archive was pre-cached on `ubuntu-heshi`,
   official prepare completed, and the MLAgentBench `debug` task produced a
   scored official baseline and co-pilot-selected branch: the starter baseline
   scored `0.5103` test accuracy and the co-pilot-selected branch scored
   `0.7782`, delta `+0.2679`, under the same official evaluator. The same
   branch was then rerun with two additional seeds, scoring `0.7709` and
   `0.7738`; the three-seed mean is `0.7743`, minimum `0.7709`, and sample std
   `0.003676`. An additional
   official `imdb` probe repaired the missing `datasets` dependency but failed
   when the Ubuntu host could not reach HuggingFace, so it is still reported as
   setup evidence only. A CLRS probe repaired the earlier dependency gap by installing
   `dm-clrs`, `jax`, `tensorflow`, and related packages; MLAgentBench reached
   the CLRS task prompt and launched `train.py`, but the CPU-only baseline
   timed out at 900 seconds without `checkpoints/best.pkl`. A reduced
   feasibility configuration (`train_steps=1`, `train_lengths=4`,
   `batch_size=1`, `hidden_size=16`) also timed out before writing
   `spec_list.pkl`, so CLRS is setup/cost evidence rather than a scored result.
   A house-price setup probe reached the official MLAgentBench prepare script,
   but the task requires the Kaggle CLI and likely Kaggle account/rule consent;
   it is therefore logged as a credential-bound official benchmark blocker, not
   as a score. The current official CIFAR result is still one task, even though
   it now has three co-pilot-selected seeds; another official task or a larger
   task portfolio is needed before claiming broad MLAgentBench coverage.
5. **ScienceAgentBench single task**: first download the verified benchmark
   artifacts on the Ubuntu host. A metadata setup probe confirmed that the
   repository is present but HuggingFace metadata access fails from the Ubuntu
   host with network unreachable, so ScienceAgentBench remains a planned
   benchmark rather than a scored result.
6. **MLE-bench Lite dry run or one task**: use only if API/compute budget allows.
7. **PaperBench-inspired rubric audit**: do not run full PaperBench initially;
   instead borrow its hierarchical rubric idea for manuscript claim auditing.

## Primary Sources

- MLE-bench: https://github.com/openai/mle-bench
- MLAgentBench: https://github.com/snap-stanford/MLAgentBench
- ScienceAgentBench: https://github.com/OSU-NLP-Group/ScienceAgentBench
- PaperBench: https://openai.com/index/paperbench/
- AIRS-Bench: https://github.com/facebookresearch/airs-bench
