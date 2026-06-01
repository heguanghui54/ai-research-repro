# Benchmark-to-Claim Matrix

This matrix keeps benchmark choice tied to the paper's claims. Co-Pilot AI
Scientist v3 should not be evaluated by defaulting to whichever benchmark is
easiest to run. Each benchmark is included only if it measures a specific part
of the system claim.

| Claim family | Benchmark or probe | Current evidence | What it supports | What it does not prove yet |
| --- | --- | --- | --- | --- |
| AI Scientist-v2 branch-gate feasibility | FML-bench `Causality_causalml` | Live two-draft branch gate, selected-snapshot continuation, and two matched autonomous four-step baselines | A human branch gate can be inserted into real AI Scientist-v2-style logs and continued from the selected snapshot | General human-gate superiority; the two matched pairs are mixed and the mean test MAE slightly favors autonomous |
| Evaluator-gate necessity | FML-bench `Fairness_fairlearn` | Failed two-draft extension plus repair/degenerate-predictor analysis | Gates must reject non-executable branches and metric-gaming fairness solutions before continuation | A successful fairness-task improvement |
| AlphaEvolve-style subproblem search | OpenEvolve function minimization and knapsack | Direct edit beats/matches tiny function search, while OpenEvolve improves the richer knapsack heuristic to 0.999439 average optimality ratio | Program search should be controlled by an escalation gate and can help on richer machine-gradeable subproblems | That OpenEvolve should always replace direct editing |
| Non-FML ML experimentation | MLAgentBench `vectorization` plus controlled evaluator | Official baseline runs; controlled OpenEvolve search keeps correct programs in 8/8 seeds with median runtime 0.024581 seconds vs. 3.261186 starter runtime | Program-search escalation works beyond FML-bench on correctness-gated ML code optimization | Whole-paper quality improvement or robust success under larger official MLAgentBench tasks |
| Non-runtime modeling boundary | sklearn diabetes tabular regression probe | Direct rewrite and three OpenEvolve seeds all improve from RMSE 78.572189 to roughly 55.9; direct rewrite matches median OpenEvolve | Direct editing can be enough for standard small modeling changes, so the escalation gate must be selective | Official benchmark performance or a program-search advantage |
| Scientific workflow benchmark expansion | ScienceAgentBench setup probe | Repository present, but verified artifacts and HuggingFace metadata are unavailable from the Ubuntu host | The benchmark is relevant but currently blocked; setup failures are logged instead of inflated into scores | Any ScienceAgentBench task score |
| Higher-cost end-to-end ML engineering | MLE-bench Lite, PaperBench, AIRS-Bench | Not run in the current budget | Stretch targets for future top-conference-level evaluation | Any current empirical claim |

## Selection Rule

Future runs should be selected by the weakest unsupported claim, not by
convenience. The next highest-value run is a single online trajectory with
idea, evaluator, branch, program-search, and claim gates active in one
continuous experiment, followed by a matched autonomous baseline under the same
budget. After that, the benchmark suite should add at least one scored official
non-FML task that exercises end-to-end experimentation rather than only a
controlled subproblem.
