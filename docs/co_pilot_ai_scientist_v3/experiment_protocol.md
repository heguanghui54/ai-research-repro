# Experiment Protocol

## Goal

Evaluate whether structured human intervention nodes improve automated research
quality in an AI Scientist-v2-style pipeline.

## System Variants

1. **Autonomous baseline**: AI Scientist-v2-style loop with no human gates.
2. **Idea gate**: human reviews and edits candidate hypotheses before
   experiments begin.
3. **Branch gate**: human reviews top tree-search branches after an initial
   budget and chooses which branches receive deeper search.
4. **Evaluator gate**: human reviews the metric/evaluator design before
   expensive runs.
5. **Claim gate**: human audits the generated paper for unsupported claims and
   forces revisions.
6. **Full co-pilot v3**: idea, branch, evaluator, and claim gates enabled,
   with OpenEvolve used as the open-source AlphaEvolve-style implementation for
   machine-gradeable subproblems.

## Benchmark Selection

The benchmark suite is selected by claim type rather than by convenience. See
`benchmark_selection.md` for the full matrix. FML-bench is useful but not
sufficient by itself.

### Tier A: Current Runnable Evidence

- **FML-bench small tasks**:
  - causality/causalml smoke task;
  - fairness/fairlearn smoke task.
  - Role: branch-gate and selected-branch continuation evidence for
    AI Scientist-v2-style search.
  - Current status: two Causality matched-budget pairs are archived. Pair 1
    favors the human-gated path on test MAE (`0.402170` vs. `0.421474`), while
    Pair 2 favors the autonomous path (`0.646224` vs. `0.595685`). More tasks,
    seeds, and budget schedules are still required.
- **OpenEvolve-controlled tasks**:
  - function minimization;
  - 0/1 knapsack heuristic search.
  - Role: AlphaEvolve-style programmatic search, direct-edit ablation, and
    program-search escalation gate.

### Tier B: Recommended Next Benchmarks

- **MLAgentBench**:
  - Role: broader end-to-end ML experimentation outside the FML-bench stack.
  - Current status: the lightweight `vectorization` task now has a controlled
    correctness-gated comparison. Direct DeepSeek rewrite failed the gate, while
    eight three-iteration OpenEvolve-style seeds all retained correct best
    programs and improved over the starter. The median best runtime is
    `0.024581` seconds versus `3.261186` seconds for the starter.
- **ScienceAgentBench**:
  - Role: data-driven scientific discovery tasks extracted from publications,
    useful for evaluator gates and claim-support checks.
  - Current status: the code repository is present on `ubuntu-heshi`, but the
    full verified benchmark artifacts are not yet downloaded, so no
    ScienceAgentBench score is reported.

### Tier C: High-Cost / Stretch Benchmarks

- **MLE-bench Lite**:
  - Role: Kaggle-style long-horizon ML engineering; high signal but expensive.
- **PaperBench**:
  - Role: paper-to-code replication and hierarchical rubric grading; useful as
    a model for claim-audit rubrics even before full runs.
- **AIRS-Bench**:
  - Role: full ML research lifecycle evaluation; good stretch target if setup
    and compute budget permit.

## Metrics

- **Task metric**: benchmark-specific validation and test score.
- **Paper score**: expert rubric from 1 to 5 for novelty, rigor, clarity,
  evidence, and reproducibility.
- **Claim support score**: percentage of manuscript claims backed by logs,
  metrics, citations, or explicit human decisions.
- **Search efficiency**: best score per API dollar, wall-clock hour, and valid
  candidate program.
- **Human attention cost**: minutes and number of edits per gate.
- **Diversity**: number of distinct surviving hypotheses or branch families.

## Ablations

- Remove AI Co-Scientist-style debate while keeping human gates.
- Remove human gates while keeping multi-agent debate.
- Replace AlphaEvolve/OpenEvolve subproblem search with direct LLM edits.
- Replace OpenEvolve MAP-Elites/island search with a simple repeated-sampling
  LLM edit baseline using the same evaluator and iteration budget.
- Move human branch selection earlier or later in the tree search.

## Robustness Checks

- Run at least two random seeds per small task when compute allows.
- Repeat one task with DeepSeek and one Monica-routed frontier model if API
  budget allows.
- Check whether gains persist when the human gate can only choose among
  structured options rather than freely rewriting the system plan.

## Failure Analysis

Record every failed branch with:

- prompt and model used;
- code diff or hypothesis text;
- evaluator output;
- human gate decision if present;
- reason the branch was pruned;
- whether the branch suggests a future research direction.

## Minimum Evidence for a First Paper Draft

- At least two runnable tasks from Tier A with logged autonomous and
  human-gated variants. The current Causality matched pairs count as an initial
  matched probe but not as a broad benchmark.
- One ablation showing which human gate matters most.
- One OpenEvolve or equivalent programmatic-search demonstration.
- A justified plan and at least one setup/baseline probe for a Tier B benchmark
  beyond FML-bench.
- Bilingual manuscript that explicitly separates verified findings from
  proposed architecture.

## OpenEvolve Integration Plan

Because AlphaEvolve's official core code is unavailable, the reproducible system
will use OpenEvolve as the implementation substrate for the programmatic-search
module.

1. Install on the Ubuntu host:

```bash
python3 -m pip install openevolve
```

2. Route models through an OpenAI-compatible endpoint. For Monica, use the
   Monica base URL and API key exposed in the global environment:

```yaml
llm:
  api_base: "https://openapi.monica.im/v1"
  model: "gpt-4o-mini"
```

3. Run a smoke or controlled task before using it inside the research loop.
   The project wrapper uses OpenEvolve's Python API directly:

```bash
python3 scripts/run_openevolve_program_search.py \
  --initial-program docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/initial_program.py \
  --evaluator docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/evaluator.py \
  --output-dir /tmp/knapsack_openevolve_5iter/run \
  --iterations 5 \
  --provider deepseek \
  --model deepseek-chat
```

4. Wrap the resulting best program and score as an AI Scientist-v3 branch
   artifact:

```json
{
  "module": "openevolve",
  "subproblem_id": "function_minimization_smoke",
  "initial_score": null,
  "best_score": null,
  "iterations": 20,
  "best_program_path": "",
  "evaluator_path": "",
  "human_gate_id": "program_search_gate_001"
}
```

5. Compare against a direct LLM-edit baseline with the same evaluator and budget.

## MLAgentBench Non-FML Probe

The first Tier B feasibility probe uses MLAgentBench `vectorization`, because
it is machine-gradeable by runtime and cheap enough for repeated ablations.

Baseline run on the Ubuntu host:

```bash
cd /home/heshi/work/bench-probes/MLAgentBench
. .venv/bin/activate
python -u -m MLAgentBench.runner \
  --python "$(which python)" \
  --task vectorization \
  --device 0 \
  --log-dir /home/heshi/work/copilotv3-mlagentbench-vectorization-baseline \
  --work-dir /home/heshi/work/copilotv3-mlagentbench-vectorization-workspace \
  --agent-type Agent \
  --max-steps 1 \
  --agent-max-steps 1
python -m MLAgentBench.eval \
  --log-folder /home/heshi/work/copilotv3-mlagentbench-vectorization-baseline \
  --task vectorization \
  --output-file /home/heshi/work/copilotv3-mlagentbench-vectorization-baseline-eval.json
```

Archived official baseline: final runtime score `3.17250394821167` seconds and
total benchmark time `3.3655309677124023` seconds. Lower is better. The
controlled evaluator adds correctness checking and produces the comparison
summarized in `experiments/mlagentbench_vectorization_comparison.md`.

For the OpenEvolve-controlled version, run explicit seeds with:

```bash
python scripts/run_openevolve_program_search.py \
  --initial-program docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_task/initial_program.py \
  --evaluator docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_task/evaluator.py \
  --output-dir docs/co_pilot_ai_scientist_v3/experiments/mlagentbench_vectorization_openevolve_3iter_seed123 \
  --iterations 3 \
  --random-seed 123 \
  --provider deepseek \
  --model deepseek-chat
```

The archived seed set (`0`, `1`, `2`, `3`, `4`, `7`, `42`, `123`) retained
correct best programs in 8 of 8 runs and improved over the controlled starter in
8 of 8 runs. The median best runtime is `0.024580717086791992` seconds, a
median speedup of about `132.67x`. Treat this as stronger but still
seed-sensitive pilot evidence, not as a settled cross-task result.
