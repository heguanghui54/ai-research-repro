# Top-Conference Readiness Audit

Audit date: 2026-06-01

This audit checks the current Co-Pilot AI Scientist v3 package against the
original project objective. It is intentionally strict: an item is marked
complete only when current artifacts prove it, not when the manuscript intends
to do it later.

## Summary

| Requirement | Current status | Evidence | Next action |
| --- | --- | --- | --- |
| English paper PDF | Satisfied as artifact | `build/co_pilot_ai_scientist_v3_en.pdf` exists and is rebuilt from `paper_en.md`. | Keep synchronized with later evidence. |
| Chinese paper PDF | Satisfied as artifact | `build/co_pilot_ai_scientist_v3_zh.pdf` exists and is rebuilt from `paper_zh.md`. | Keep synchronized with later evidence. |
| English and Chinese usage documents | Satisfied as artifact | `usage_en.md`, `usage_zh.md`, `RUNBOOK_EN.md`, `RUNBOOK_ZH.md`. | Keep commands aligned with scripts and remote paths. |
| Reusable Codex skill | Satisfied as artifact and local smoke | `skills/co-pilot-ai-scientist-v3/SKILL.md` plus templates; clean clone verifies the skill files listed in the manifest are present; `skill_reuse_smoke_audit.md` instantiates a new task spec and validates a generated gate log. | Run a live skill invocation on a new task with model calls before calling the workflow production-ready. |
| GitHub push | Satisfied for current branch | Branch `codex/co-pilot-ai-scientist-v3` is pushed to `heguanghui54/ai-research-repro`; clean clone at commit `6dfbdc8ee` succeeded. | Merge or tag a stable release when the package is ready. |
| AI Co-Scientist-style direction finding and hypothesis organization | Partially supported | Candidate files, literature matrix, idea gate, scientific-taste gate. | Run a fresh online hypothesis-generation front end with logs. |
| AI Scientist-v2-style experiment execution and paper writing | Partially supported | FML-bench runs, matched Causality pairs, generated paper drafts and PDFs. | Demonstrate one continuous paper-generating trajectory from new hypothesis to final claim-audited manuscript. |
| AlphaEvolve-style deep search on automatically evaluated subproblems | Supported narrowly | OpenEvolve function minimization, knapsack, Max-Cut, MLAgentBench vectorization, sklearn diabetes probes. | Add stronger selection rules and larger budgets where search space warrants it. |
| Human participation at creative or key decision nodes | Supported as logging and orchestration | Human gate schema, 8 standalone gate logs, 10 embedded trajectory gates, one complete scientific-taste prior record. | Record future gates prospectively with both `taste_insight` and `attention_cost`. |
| Human taste/insight as distinct from generic approval | Partially supported | IGRE framing, taste rubric, scientific-taste prior gate, taste coverage audit. | Show downstream effects against autonomous baselines; current evidence is logging, not performance. |
| Human attention cost measurement | Tooling supported; real gates not yet measured | Attention-cost audit covers 18 real gates and finds 0 complete measured records. `attention_cost_logging_smoke_audit.md` shows a synthetic gate can be generated with complete prospective timing fields. | Use the logging tool during future live gates; do not count synthetic smoke as performance evidence. |
| Joint attention+taste gate logging | Tooling supported; real matched run not yet measured | `attention_taste_logging_smoke_audit.md` shows `create_human_gate_log.py` can generate a schema-compatible gate with complete `attention_cost` and `taste_insight`. | Use `--require-complete-attention` and `--require-complete-taste` during the next prospective matched-budget package. |
| Prospective matched-budget evidence package | Passes only as controlled micro-pilot | `prospective_matched_budget_package_audit.md` now finds 1 passing package: `prospective_matched_micro_pilot_20260602_000001`, with complete `attention_cost` and `taste_insight`, matched baseline, claim audit, and same-run manuscript. | Upgrade this from a controlled Max-Cut micro-pilot to an AI Scientist-v2/FML or MLAgentBench package before upgrading performance or paper-quality claims. |
| Evidence that human collaboration writes better papers | Not yet supported | Claim audit marks this as unsupported; paper-quality reviews remain mixed. | Run expert/rubric-based paper-quality scoring on matched autonomous vs co-pilot outputs. |
| Evidence that full Co-Pilot v3 outperforms autonomous AI Scientist-v2 | Not yet supported | FML matched pairs are mixed; online smoke comparison is negative. | Run multi-task, multi-seed matched-budget comparisons. |
| Benchmark coverage beyond FML-Bench | Partially supported | MLAgentBench vectorization is scored; sklearn diabetes/Max-Cut/OpenEvolve tasks broaden subproblem evidence; CIFAR10/debug, IMDB, and ScienceAgentBench are setup probes only. | Obtain a second scored official non-FML benchmark when data access permits. |
| Top-conference-level empirical support | Not yet supported | Monica-routed reviewers agree broader matched-budget evidence and full trajectory are missing; Claude rejects for strong venue. | Treat current paper as a strong pilot/reproducibility package, not a completed top-conference submission. |
| Independent clean-clone artifact reproducibility | Supported for current artifacts | `clean_clone_reproducibility_audit.md`: fresh GitHub clone rebuilt both PDFs, reran gate audits, and found 266/266 manifest artifacts and reran the reusable-skill smoke audit. | Still needs independent rerun of remote Ubuntu experiments for stronger reproduction. |

## Interpretation

The package now satisfies the requested artifact pipeline: bilingual papers,
usage guides, a reusable Codex skill, reproducibility artifacts, and a pushed
GitHub branch. It also has a distinctive method name and mechanism:
Insight-Gated Research Evolution (IGRE), with scientific taste/insight logged
as a high-variance search prior rather than as preference labeling or generic
approval.

The evidence bar for the original target is still higher than the current
package. The strongest current claim is:

> IGRE is a reproducible co-pilot architecture and pilot evidence package for
> inserting human scientific taste, evaluator stress tests, frontier steering,
> verifiable micro-evolution, and claim calibration into AI Scientist-v2-style
> research loops.

The current package should not yet claim:

- human gates improve average benchmark performance;
- human gates improve paper quality;
- the full co-pilot system outperforms autonomous AI Scientist-v2;
- human attention efficiency has been measured;
- the paper is ready for a strong ML/NLP systems conference without further
  experiments.

The next evidence milestone is a substantive prospective matched-budget package
that passes `scripts/audit_prospective_matched_budget_package.py` on an
AI Scientist-v2/FML or MLAgentBench task. The controlled micro-pilot proves the
evidence shape can be generated; it does not yet prove paper-quality gains,
attention efficiency, or superiority over autonomous AI Scientist-v2.
