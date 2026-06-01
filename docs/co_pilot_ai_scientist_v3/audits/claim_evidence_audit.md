# Claim-Evidence Audit

Audit date: 2026-06-01

Reviewer routes:

- Human/Codex rules audit against local artifacts.
- Monica OpenAI-compatible `gpt-4o-mini` review:
  `audits/claim_audit_monica_gpt4o_mini.md`.

## Claim Table

| Claim | Evidence | Status | Required paper treatment |
| --- | --- | --- | --- |
| Co-Pilot AI Scientist v3 is a modular human-in-the-loop architecture combining AI Co-Scientist, AI Scientist-v2, and AlphaEvolve-style ideas. | `paper_en.md`, `literature_matrix.md`, `skills/co-pilot-ai-scientist-v3/SKILL.md` | Supported as design contribution | Present as architecture/proposal, not as proven performance result. |
| OpenEvolve can serve as the reproducible AlphaEvolve-style substrate because official AlphaEvolve core code is unavailable. | `usage_en.md`, `usage_zh.md`, `repro_manifest.json`, OpenEvolve experiment artifacts | Supported | Use "AlphaEvolve-style" and "OpenEvolve-based"; do not claim official AlphaEvolve reproduction. |
| Programmatic search is useful on some machine-gradeable subproblems. | Knapsack: direct `0.995270`, OpenEvolve `0.999439`; MLAgentBench controlled starter `3.261186s`; OpenEvolve seeds 42/7/123 best runtimes `0.051882s`, `2.984610s`, `0.031783s`; direct rewrite invalid. | Supported narrowly, with seed sensitivity | Limit to "some machine-gradeable subproblems"; do not claim downstream paper-quality improvement or deterministic reliability under tiny budgets. |
| Programmatic search should be gated rather than always used. | Function-minimization direct baseline `0.038021` beats 1-iter OpenEvolve `0.037816` and 5-iter OpenEvolve `0.038007`; knapsack/MLAgentBench favor OpenEvolve. | Supported | State as a design lesson: use escalation gate based on evaluator richness and budget. |
| AI Scientist-v2 branch frontiers can expose actionable human gate points. | Retrospective FML replay and live two-draft Causality probe with logged branch metrics. | Supported as feasibility | Present as feasible insertion point, not proof that humans improve outcomes generally. |
| Selected-branch continuation improves over the live two-draft and earlier smoke runs. | Snapshot-seeded continuation test MAE `0.402170` vs live two-draft test MAE `0.640451` and earlier four-step smoke test MAE `0.617719`. | Partially supported | Keep caveat: one task/seed, snapshot seeding, not matched autonomous budget. |
| Human gates improve paper quality. | No expert or rubric-based paper-quality scores yet. | Unsupported | Keep only as hypothesis/future evaluation target. |
| Full Co-Pilot AI Scientist v3 outperforms autonomous AI Scientist-v2. | No matched multi-task autonomous vs full co-pilot benchmark yet. | Unsupported | Do not claim as result. State as target claim requiring future evidence. |
| The current paper is top-conference ready. | Pilot evidence exists, but no statistical tests, broad benchmark suite, or independent paper scoring. | Unsupported | Present as a research package moving toward top-conference strength, with remaining requirements. |

## Required Edits Applied

- Reframe empirical statements as pilot evidence.
- Separate architecture contributions from performance results.
- Keep "improves paper quality" and "outperforms autonomous AI Scientist-v2" as hypotheses, not conclusions.
- Report the MLAgentBench seed-7 non-improvement alongside successful seeds.
- Add the Monica model audit as an artifact rather than silently relying on it.

## Remaining Evidence Needed

- More matched autonomous vs human-gated comparisons across tasks and seeds.
- Native tree-object resume instead of snapshot-seeded branch continuation, if feasible.
- Expert or rubric-based paper-quality scoring.
- A second non-FML benchmark task or ScienceAgentBench-style scientific workflow.
- GitHub publication and independent reproducibility check.
