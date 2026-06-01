# Claim-Evidence Audit

Audit date: 2026-06-01

Reviewer routes:

- Human/Codex rules audit against local artifacts.
- Monica OpenAI-compatible `gpt-4o-mini` review:
  `audits/claim_audit_monica_gpt4o_mini.md`.
- Monica-routed paper-quality reviews:
  `audits/paper_quality_reviews/gpt-4o-mini.md`,
  `audits/paper_quality_reviews/claude-3-7-sonnet-latest.md`, and
  `audits/paper_quality_review_summary.md`.

## Claim Table

| Claim | Evidence | Status | Required paper treatment |
| --- | --- | --- | --- |
| Co-Pilot AI Scientist v3 is a modular human-in-the-loop architecture combining AI Co-Scientist, AI Scientist-v2, and AlphaEvolve-style ideas. | `paper_en.md`, `literature_matrix.md`, `skills/co-pilot-ai-scientist-v3/SKILL.md` | Supported as design contribution | Present as architecture/proposal, not as proven performance result. |
| OpenEvolve can serve as the reproducible AlphaEvolve-style substrate because official AlphaEvolve core code is unavailable. | `usage_en.md`, `usage_zh.md`, `repro_manifest.json`, OpenEvolve experiment artifacts | Supported | Use "AlphaEvolve-style" and "OpenEvolve-based"; do not claim official AlphaEvolve reproduction. |
| Programmatic search is useful on some machine-gradeable subproblems. | Knapsack: direct `0.995270`, OpenEvolve `0.999439`; Max-Cut: starter `0.734680`, direct `0.962237`, OpenEvolve `0.970833`; MLAgentBench controlled starter `3.261186s`; eight OpenEvolve seeds all retained correct best programs with median best runtime `0.024581s`; direct rewrite invalid; sklearn diabetes OpenEvolve seeds improve mean predictor RMSE `78.572189` to median `55.895460`. | Supported narrowly, with seed sensitivity | Limit to "some machine-gradeable subproblems"; do not claim downstream paper-quality improvement or deterministic reliability under tiny budgets. |
| Programmatic search should be gated rather than always used. | Function-minimization direct baseline `0.038021` beats 1-iter OpenEvolve `0.037816` and 5-iter OpenEvolve `0.038007`; sklearn diabetes direct rewrite matches median OpenEvolve RMSE `55.895460`; knapsack/MLAgentBench favor OpenEvolve; Max-Cut favors OpenEvolve but only by `0.008596`. | Supported | State as a design lesson: use escalation gate based on evaluator richness, expected search value, and budget. |
| Benchmark expansion beyond FML-bench is underway but incomplete. | MLAgentBench vectorization has an official baseline and controlled eight-seed probe. MLAgentBench CIFAR10/debug setup repaired `torchvision` but stopped at slow dataset download. ScienceAgentBench repository is present, but verified artifacts are missing and HuggingFace metadata was unreachable from `ubuntu-heshi`. | Supported as setup/progress evidence only | Do not report CIFAR10 or ScienceAgentBench scores. Use these probes to justify next evidence requirements. |
| The full set of proposed gate types can be represented as structured artifacts. | `idea_gate_001.json`, `scientific_taste_prior_benchmark_portfolio_001.json`, `evaluator_gate_fairness_metric_guardrail.json`, `branch_gate_causality_online_two_drafts.json`, `program_search_gate_001.json`, `claim_gate_001.json`, `full_gate_retrospective_trajectory.md`, and `full_gate_executable_trace/trajectory.json`. | Supported as retrospective/executable artifact evidence | Present as an auditable and rerunnable gate-chain artifact, not as a completed online end-to-end run. |
| All five proposed gate types can be exercised in one fresh online smoke trajectory. | `online_full_gate_smoke_20260601_145720/trajectory.json`: fresh FML two-draft frontier, selected-snapshot continuation, one-iteration OpenEvolve knapsack, and claim audit on `ubuntu-heshi`. | Supported as online orchestration smoke evidence | Present as feasibility only; the one-step continuation worsened held-out test MAE and no matched autonomous baseline was run for this exact trajectory. |
| The first online full-gate smoke outperforms an autonomous baseline. | `online_smoke_matched_autonomous_comparison.md`: human-gated continuation test MAE `0.862015`; autonomous 3-step test MAE `0.428516`. | Contradicted by current smoke evidence | Report as a negative result. Do not claim performance improvement from the online smoke. |
| The current manuscript is ready for a strong ML/NLP systems venue. | Refreshed Monica-routed paper-quality reviews after Max-Cut and matched online-smoke evidence: `gpt-4o-mini` gives `Weak accept`, while `claude-3-7-sonnet-latest` gives `Reject` with rigor/evidence scores `1/5`. | Not supported | Treat the current package as a strong pilot/reproducibility artifact. Required next steps are larger matched-budget experiments, a full paper-generating trajectory, attention-cost measurement, and clearer paper structure. |
| Human scientific taste/insight is logged distinctly from generic approval. | `taste_insight_rubric.md`, `scientific_taste_prior_benchmark_portfolio_001.json`, and `audits/taste_insight_coverage_audit.md`: 18 gate records audited, 1 complete scientific-taste prior record, 17 older records without taste fields. | Supported as logging/readiness evidence | Present as operationalization of IGRE's distinctive human role, not as evidence that taste improved downstream outcomes. |
| Human attention cost is measured for existing gates. | `audits/human_gate_attention_cost_audit.md`: 18 gate records audited, including 8 standalone gate logs and 10 embedded trajectory gates across 2 trajectory artifacts; 0 complete attention-cost records. | Not supported | Report as a measurement-readiness gap. Future prospective matched-budget runs must record active review minutes, latency, options reviewed, artifacts reviewed, and decision count. |
| AI Scientist-v2 branch frontiers can expose actionable human gate points. | Retrospective FML replay and live two-draft Causality probe with logged branch metrics. | Supported as feasibility | Present as feasible insertion point, not proof that humans improve outcomes generally. |
| Evaluator gates must reject non-executable and metric-gaming branches before continuation. | `fml_fairness_gated_drafts_failed/`: two Fairness_fairlearn drafts failed validation due Fairlearn/sklearn API incompatibilities before producing a score. `fml_fairness_evaluator_gate_repair.md`: an executable repaired candidate worsened test demographic parity difference (`0.317603` vs baseline `0.173030`), while a degenerate all-negative predictor achieved `0.000000` demographic parity difference but only `0.500000` balanced accuracy. | Supported as failure-mode/evaluator-design evidence | Present as a gate-design lesson. Do not count the Fairness probe as matched-budget performance evidence or a fairness improvement. |
| Matched-budget human-gated branch continuation has mixed evidence against autonomous AI Scientist-v2. | Pair 1: human-gated test MAE `0.402170`, autonomous test MAE `0.421474`. Pair 2: human-gated test MAE `0.646224`, autonomous test MAE `0.595685`. Two-pair mean favors autonomous by `0.015618` MAE. | Supported as mixed evidence | Present as feasibility plus mixed outcome; do not claim human-gate superiority. |
| Human gates improve paper quality. | No expert or rubric-based paper-quality scores yet. | Unsupported | Keep only as hypothesis/future evaluation target. |
| Full Co-Pilot AI Scientist v3 outperforms autonomous AI Scientist-v2. | No matched multi-task autonomous vs full co-pilot benchmark yet. | Unsupported | Do not claim as result. State as target claim requiring future evidence. |
| The current paper is top-conference ready. | Pilot evidence exists, but no statistical tests or broad matched-budget benchmark suite. GPT-4o-mini paper review gives weak accept; Claude 3.7 Sonnet review gives reject for strong ML/NLP systems venue. | Unsupported | Present as a research package moving toward top-conference strength, with remaining requirements. |
| The current package satisfies the artifact-delivery portion of the objective. | `top_conference_readiness_audit.md`: bilingual PDFs, bilingual usage docs, reusable skill, reproducibility package, and pushed GitHub branch are present. | Supported for artifacts only | Do not confuse artifact completion with top-conference empirical readiness. |

## Required Edits Applied

- Reframe empirical statements as pilot evidence.
- Separate architecture contributions from performance results.
- Keep "improves paper quality" and "outperforms autonomous AI Scientist-v2" as hypotheses, not conclusions.
- Report the MLAgentBench seed-7 weak improvement and seed-1 weaker improvement
  alongside the stronger successful seeds.
- Add the Monica model audit as an artifact rather than silently relying on it.
- Add paper-quality review artifacts and explicitly report that reviewers disagree
  on recommendation but agree on the need for broader matched-budget evidence.
- Add the second matched FML Causality pair and revise the manuscript from a
  single positive matched result to mixed paired evidence.
- Add the Fairness evaluator-gate repair probe and require utility floors for
  fairness metrics that can be gamed by degenerate classifiers.
- Add setup probes for a second official MLAgentBench task and ScienceAgentBench
  metadata access; keep both as blockers, not scores.
- Add idea, evaluator, and claim gate logs plus a retrospective full-gate
  trajectory; keep the online four-loop run as future evidence.
- Add `scripts/run_full_gate_trajectory.py` and
  `experiments/full_gate_executable_trace/trajectory.json` as a reproducible
  artifact replay of the gate chain, while preserving the caveat that it is not
  a fresh online run.
- Add `scripts/run_online_full_gate_smoke.py` and
  `experiments/online_full_gate_smoke_20260601_145720/` as a first fresh online
  five-gate smoke trajectory; report it as orchestration feasibility and
  negative continuation evidence, not as a win.
- Add `online_smoke_autonomous_matched_3step/` and
  `online_smoke_matched_autonomous_comparison.md`; report the same-FML-step
  comparison as a negative performance result for the human-gated continuation.
- Add `scientific_taste_prior_benchmark_portfolio_001.json` and
  `audits/taste_insight_coverage_audit.md`; report one complete taste/insight
  record as logging evidence, not as downstream performance evidence.
- Add `audits/top_conference_readiness_audit.md` to separate delivered
  artifacts from remaining top-conference evidence requirements.

## Remaining Evidence Needed

- More matched autonomous vs human-gated comparisons across tasks and seeds; two
  paired Causality runs are archived but remain insufficient and mixed.
- Native tree-object resume instead of snapshot-seeded branch continuation, if feasible.
- Expert or rubric-based paper-quality scoring.
- A second scored non-FML benchmark task. Current CIFAR10/debug and
  ScienceAgentBench probes are setup evidence only.
- A larger online four-loop end-to-end trajectory that goes from new hypothesis
  generation to final manuscript production, with a matched autonomous baseline
  under the same budget.
- Independent reproducibility check from a clean clone or separate machine.
