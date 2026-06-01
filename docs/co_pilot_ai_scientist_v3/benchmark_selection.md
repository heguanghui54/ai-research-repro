# Benchmark Selection Strategy

Co-Pilot AI Scientist v3 should not be evaluated only on FML-bench. FML-bench
is useful because it is already runnable in the current Ubuntu environment and
exercises AI Scientist-v2-style branch search, but the paper's claims span more
than one benchmark can measure.

The benchmark suite is therefore selected by claim type.

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
| A | OpenEvolve-controlled tasks | Machine-gradeable program search | AlphaEvolve-style escalation gate and direct-edit ablation | Runnable and already used |
| B | MLAgentBench | End-to-end ML experimentation agents | Broader ML experiment-loop validation beyond FML-bench | Recommended next benchmark |
| B | ScienceAgentBench | Data-driven scientific discovery code tasks from publications | Non-FML scientific workflow validation, especially evaluator/claim gates | Recommended next benchmark |
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

1. **MLAgentBench vectorization extension**: baseline, direct LLM rewrite, and
   OpenEvolve-style runtime optimization now run under a correctness-gated
   evaluator with a first three-seed robustness probe; next add a second
   MLAgentBench task or a larger matched seed budget.
2. **ScienceAgentBench single task**: use one data-driven discovery task to test
   evaluator and claim gates in a more science-like setting.
3. **MLE-bench Lite dry run or one task**: use only if API/compute budget allows.
4. **PaperBench-inspired rubric audit**: do not run full PaperBench initially;
   instead borrow its hierarchical rubric idea for manuscript claim auditing.

## Primary Sources

- MLE-bench: https://github.com/openai/mle-bench
- MLAgentBench: https://github.com/snap-stanford/MLAgentBench
- ScienceAgentBench: https://github.com/OSU-NLP-Group/ScienceAgentBench
- PaperBench: https://openai.com/index/paperbench/
- AIRS-Bench: https://github.com/facebookresearch/airs-bench
