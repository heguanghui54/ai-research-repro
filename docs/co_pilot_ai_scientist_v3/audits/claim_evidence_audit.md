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
| Programmatic search is useful on some machine-gradeable subproblems. | Knapsack: direct `0.995270`, OpenEvolve `0.999439`; MLAgentBench controlled starter `3.261186s`; eight OpenEvolve seeds all retained correct best programs with median best runtime `0.024581s`; direct rewrite invalid; sklearn diabetes OpenEvolve seeds improve mean predictor RMSE `78.572189` to median `55.895460`. | Supported narrowly, with seed sensitivity | Limit to "some machine-gradeable subproblems"; do not claim downstream paper-quality improvement or deterministic reliability under tiny budgets. |
| Programmatic search should be gated rather than always used. | Function-minimization direct baseline `0.038021` beats 1-iter OpenEvolve `0.037816` and 5-iter OpenEvolve `0.038007`; sklearn diabetes direct rewrite matches median OpenEvolve RMSE `55.895460`; knapsack/MLAgentBench favor OpenEvolve. | Supported | State as a design lesson: use escalation gate based on evaluator richness, expected search value, and budget. |
| AI Scientist-v2 branch frontiers can expose actionable human gate points. | Retrospective FML replay and live two-draft Causality probe with logged branch metrics. | Supported as feasibility | Present as feasible insertion point, not proof that humans improve outcomes generally. |
| Evaluator gates must reject non-executable and metric-gaming branches before continuation. | `fml_fairness_gated_drafts_failed/`: two Fairness_fairlearn drafts failed validation due Fairlearn/sklearn API incompatibilities before producing a score. `fml_fairness_evaluator_gate_repair.md`: an executable repaired candidate worsened test demographic parity difference (`0.317603` vs baseline `0.173030`), while a degenerate all-negative predictor achieved `0.000000` demographic parity difference but only `0.500000` balanced accuracy. | Supported as failure-mode/evaluator-design evidence | Present as a gate-design lesson. Do not count the Fairness probe as matched-budget performance evidence or a fairness improvement. |
| Matched-budget human-gated branch continuation has mixed evidence against autonomous AI Scientist-v2. | Pair 1: human-gated test MAE `0.402170`, autonomous test MAE `0.421474`. Pair 2: human-gated test MAE `0.646224`, autonomous test MAE `0.595685`. Two-pair mean favors autonomous by `0.015618` MAE. | Supported as mixed evidence | Present as feasibility plus mixed outcome; do not claim human-gate superiority. |
| Human gates improve paper quality. | No expert or rubric-based paper-quality scores yet. | Unsupported | Keep only as hypothesis/future evaluation target. |
| Full Co-Pilot AI Scientist v3 outperforms autonomous AI Scientist-v2. | No matched multi-task autonomous vs full co-pilot benchmark yet. | Unsupported | Do not claim as result. State as target claim requiring future evidence. |
| The current paper is top-conference ready. | Pilot evidence exists, but no statistical tests or broad matched-budget benchmark suite. GPT-4o-mini paper review gives weak accept; Claude 3.7 Sonnet review gives reject for strong ML/NLP systems venue. | Unsupported | Present as a research package moving toward top-conference strength, with remaining requirements. |

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

## Remaining Evidence Needed

- More matched autonomous vs human-gated comparisons across tasks and seeds; two
  paired Causality runs are archived but remain insufficient and mixed.
- Native tree-object resume instead of snapshot-seeded branch continuation, if feasible.
- Expert or rubric-based paper-quality scoring.
- A second non-FML benchmark task or a ScienceAgentBench-style scientific
  workflow after verified benchmark artifacts are downloaded.
- A complete four-loop end-to-end trajectory with all gates operating in one run.
- GitHub publication and independent reproducibility check.
