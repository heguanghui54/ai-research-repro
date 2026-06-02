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
| GitHub push | Satisfied for current branch | Branch `codex/co-pilot-ai-scientist-v3` is pushed to `heguanghui54/ai-research-repro`; clean clone at latest audited pushed commit `b06933c31` succeeded. | Merge or tag a stable release when the package is ready. |
| AI Co-Scientist-style direction finding and hypothesis organization | Partially supported with live front-end and downstream feedback probe | Candidate files, literature matrix, idea gate, scientific-taste gate, `experiments/hypothesis_frontier_smoke_20260602_021500/`, and `experiments/structured_feedback_probe_20260602_022900/`. The first uses two Monica-routed `gpt-4o-mini` calls to generate four candidate research frontiers, critique/rank them, and select `frontier_004`; the second operationalizes that frontier with five calls comparing informal feedback to IGRE-structured feedback on the same manuscript. | Compare against an autonomous hypothesis-front-end baseline and replace model-routed scoring with broader task/seed coverage plus independent expert review. |
| AI Scientist-v2-style experiment execution and paper writing | Partially supported | FML-bench runs, matched Causality pairs, generated paper drafts and PDFs. Three same-continuous-trajectory online smokes now generate co-pilot and autonomous manuscript artifacts in the same orchestrator runs; the repeated summary reports `0` co-pilot benchmark wins, `1` autonomous win, `1` tie, and `1` Fairness no-valid failure trajectory. | Scale beyond smoke budgets across more tasks/seeds and add independent paper-quality review. |
| AlphaEvolve-style deep search on automatically evaluated subproblems | Supported narrowly | OpenEvolve function minimization, knapsack, Max-Cut, MLAgentBench vectorization, sklearn diabetes probes. | Add stronger selection rules and larger budgets where search space warrants it. |
| Human participation at creative or key decision nodes | Supported as logging and orchestration | Human gate schema plus the derived Human Co-Pilot Trace Dataset: 52 gate records, 35 records with attention-cost fields, 10 records with taste/insight fields, and 4 prospective matched packages. The dataset release audit passes with 0 secret-pattern hits and 0 raw-log marker hits. | Expand beyond the single-author trace corpus and record future gates prospectively with both `taste_insight` and `attention_cost`. |
| Human taste/insight as distinct from generic approval | Partially supported | IGRE framing, taste rubric, two complete scientific-taste prior gates, taste coverage audit over 39 gates, and `human_copilot_trace_dataset.md/json`. | Show downstream effects against autonomous baselines; current evidence is mostly process/logging plus negative short-budget FML results. |
| Human attention cost measurement | Operator-recorded measurement-readiness only | Attention-cost audit covers 39 gates and finds 1 complete operator-recorded attention-cost record plus 38 incomplete records. `attention_taste_priority_gate_audit.md` records the live decision to prioritize attention/taste measurement before stronger human-efficiency claims. | Record complete timing during future prospective experiment gates; do not treat the single operator-recorded planning gate as independent human-subject or performance evidence. |
| Joint attention+taste gate logging | Operator-recorded measurement-readiness only | `attention_taste_priority_gate_audit.md` shows `create_human_gate_log.py` generated a schema-compatible live decision gate with complete `attention_cost` and `taste_insight`. | Use `--require-complete-attention` and `--require-complete-taste` during future prospective matched-budget experiment gates. |
| Prospective matched-budget evidence package | Passes with mostly negative metric outcomes | `prospective_matched_budget_package_audit.md` now finds 4 passing packages, and `prospective_matched_package_summary.md` separates their outcomes: the controlled micro-pilot favors the human-selected branch (`0.984419` vs. `0.596214` mean normalized score), two FML-bench Causality packages are negative for co-pilot performance (`0.646224` vs. `0.624703`, and `0.646224` vs. `0.296399` test MAE; lower is better), and one Fairness_fairlearn package records `abort_no_valid_branch` for the co-pilot frontier while the autonomous baseline reaches `0.172152` primary metric. | Scale beyond small negative FML runs and evaluate high-tail paper-quality outcomes before upgrading claims. |
| Evidence that human collaboration writes better papers | Weak manuscript-generation and structured-feedback probes only | The refreshed Monica-routed paper-quality review saw the prospective package summary. `gpt-4o-mini` gives `Weak accept`, while `claude-3-7-sonnet-latest` gives `Reject`. The matched mini-manuscript probe has both reviewers prefer the co-pilot mini-manuscript (`overall 4` vs. `3`). The full-manuscript generation probes render both variants into complete paper-shaped manuscripts; the latest Fairness probe scores co-pilot `4.18` vs. autonomous `4.11` on an internal rubric, while autonomous is the only variant with a valid scalar FML test result. The repeated same-continuous online smoke summary includes three paired manuscripts; Monica-routed model reviewers prefer co-pilot in `6/6` calls, but benchmark outcomes are `0` co-pilot wins, `1` autonomous win, `1` tie, and `1` no-valid failure case. The structured-feedback probe scores a same-manuscript IGRE-structured revision higher than an informal-feedback revision (`overall 5` vs. `4`), but it is model-routed and contains an internal caveat around limitation-honesty interpretation. | Run independent human expert/rubric-based paper-quality scoring on larger same-continuous-trajectory outputs across tasks/seeds. |
| Evidence that full Co-Pilot v3 outperforms autonomous AI Scientist-v2 | Not supported; current FML evidence leans autonomous | `fml_matched_comparison_summary.md` reports 1 human-gated win and 1 autonomous/tie win across two formal Causality pairs; the mean delta slightly favors autonomous. The repeated same-run online smoke summary reports `0` co-pilot wins, `1` autonomous win, `1` tie, and `1` no-valid Fairness failure case; both prospective Causality packages and the prospective Fairness invalid-continuation package are also negative for co-pilot performance. | Run multi-task, multi-seed matched-budget comparisons and evaluate high-tail scientific outputs, not only short-budget MAE. |
| Benchmark coverage beyond FML-Bench | Partially supported | MLAgentBench vectorization is scored; sklearn diabetes/Max-Cut/OpenEvolve tasks broaden subproblem evidence; CIFAR10/debug, IMDB, and ScienceAgentBench are setup probes only. | Obtain a second scored official non-FML benchmark when data access permits. |
| Top-conference-level empirical support | Not yet supported | The package now has three same-continuous-trajectory manuscript comparisons, including one Fairness no-valid failure case, and model-review probes preferring co-pilot manuscripts. The repeated benchmark aggregate is autonomous-or-tie for valid Causality rows and unknown/no-valid for Fairness, still tiny-budget. Broader matched evidence and independent human paper-quality review are still missing; Claude rejects for strong venue. | Treat current paper as a strong pilot/reproducibility package, not a completed top-conference submission. |
| Independent clean-clone artifact reproducibility | Supported for latest audited pushed artifact set | `clean_clone_reproducibility_audit.md`: fresh GitHub clone at commit `b06933c31` rebuilt both PDFs, reran gate audits over 39 gate records, rebuilt and audited the derived trace dataset, found 409/409 manifest artifacts, and reran the reusable-skill smoke audit. This audit verifies the attention/taste-priority gate in the pushed package; this metadata update itself should be re-audited after the next push. | Still needs independent rerun of remote Ubuntu experiments for stronger reproduction. |

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
