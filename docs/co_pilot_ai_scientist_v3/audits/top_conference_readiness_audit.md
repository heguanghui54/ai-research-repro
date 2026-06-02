# Top-Conference Readiness Audit

Audit date: 2026-06-02

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
| Human participation at creative or key decision nodes | Supported as logging and orchestration | Human gate schema plus the derived Human Co-Pilot Trace Dataset: 31 gate records, 14 records with attention-cost fields, 9 records with taste/insight fields, and 4 prospective matched packages. The dataset release audit passes with 0 secret-pattern hits and 0 raw-log marker hits. | Expand beyond the single-author trace corpus and record future gates prospectively with both `taste_insight` and `attention_cost`. |
| Human taste/insight as distinct from generic approval | Partially supported | IGRE framing, taste rubric, scientific-taste prior gate, taste coverage audit, and `human_copilot_trace_dataset.md/json`. | Show downstream effects against autonomous baselines; current evidence is mostly process/logging plus negative short-budget FML results. |
| Human attention cost measurement | Tooling supported; real gates not yet measured | Attention-cost audit covers 18 real gates and finds 0 complete measured records. `attention_cost_logging_smoke_audit.md` shows a synthetic gate can be generated with complete prospective timing fields. | Use the logging tool during future live gates; do not count synthetic smoke as performance evidence. |
| Joint attention+taste gate logging | Tooling supported; real matched run not yet measured | `attention_taste_logging_smoke_audit.md` shows `create_human_gate_log.py` can generate a schema-compatible gate with complete `attention_cost` and `taste_insight`. | Use `--require-complete-attention` and `--require-complete-taste` during the next prospective matched-budget package. |
| Prospective matched-budget evidence package | Passes with mostly negative metric outcomes | `prospective_matched_budget_package_audit.md` now finds 4 passing packages, and `prospective_matched_package_summary.md` separates their outcomes: the controlled micro-pilot favors the human-selected branch (`0.984419` vs. `0.596214` mean normalized score), two FML-bench Causality packages are negative for co-pilot performance (`0.646224` vs. `0.624703`, and `0.646224` vs. `0.296399` test MAE; lower is better), and one Fairness_fairlearn package records `abort_no_valid_branch` for the co-pilot frontier while the autonomous baseline reaches `0.172152` primary metric. | Scale beyond small negative FML runs and evaluate high-tail paper-quality outcomes before upgrading claims. |
| Evidence that human collaboration writes better papers | Weak manuscript-generation probes only | The refreshed Monica-routed paper-quality review saw the prospective package summary. `gpt-4o-mini` gives `Weak accept`, while `claude-3-7-sonnet-latest` gives `Reject`. The matched mini-manuscript probe has both reviewers prefer the co-pilot mini-manuscript (`overall 4` vs. `3`). The new full-manuscript generation probe renders both variants into complete paper-shaped manuscripts and scores co-pilot `4.18` vs. autonomous `4.00` on an internal rubric, while autonomous still wins the scalar FML test metric. These are archived-evidence manuscript probes, not fresh full end-to-end paper comparisons. | Run expert/rubric-based paper-quality scoring on matched autonomous vs co-pilot full manuscript outputs from fresh trajectories. |
| Evidence that full Co-Pilot v3 outperforms autonomous AI Scientist-v2 | Not supported; current FML evidence leans autonomous | `fml_matched_comparison_summary.md` reports 1 human-gated win and 1 autonomous/tie win across two formal Causality pairs; the mean delta slightly favors autonomous. The online smoke comparison, both prospective Causality packages, and the prospective Fairness invalid-continuation package are negative for co-pilot performance. | Run multi-task, multi-seed matched-budget comparisons and evaluate high-tail scientific outputs, not only short-budget MAE. |
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

The next evidence milestone is to scale beyond the single-author Codex trace
and the current negative short-budget FML evidence: more tasks, seeds, larger
budgets, fresh matched manuscript trajectories, paper-quality scoring,
independent human timing, and ideally multiple human researchers. The FML
packages prove the evidence shape can be generated on an AI Scientist-v2-style
benchmark; they currently argue against short-budget average-performance
superiority and do not prove paper-quality gains, attention efficiency, or
superiority over autonomous AI Scientist-v2.
