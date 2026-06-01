# Co-Pilot AI Scientist v3 Research Package

This package tracks the paper and reproducibility artifacts for Co-Pilot AI
Scientist v3 and its core method, Insight-Gated Research Evolution (IGRE).

## Working Title

Co-Pilot AI Scientist v3: Insight-Gated Research Evolution for Collaborative
Automated Science

## Target Claim

Automated research systems should be evaluated not only by average short-budget
benchmark score, but also by whether human scientific taste can reshape the
search frontier toward rarer, higher-novelty, higher-impact outcomes. IGRE
turns human participation into explicit, logged gates for scientific taste,
evaluator stress-testing, frontier steering, verifiable micro-evolution, and
claim calibration.

## Artifact Map

- `problem_statement.md`: precise research framing, success criteria, and risks.
- `literature_matrix.md`: how AI Co-Scientist, AI Scientist-v2, AlphaEvolve,
  Coscientist, and related systems map into this proposal.
- `architecture.md`: IGRE data-flow view of the four loops and five gates.
- `benchmark_selection.md`: tiered benchmark strategy beyond FML-bench.
- `benchmark_claim_matrix.md`: claim-to-benchmark matrix recording what each
  benchmark can and cannot prove.
- `taste_insight_rubric.md`: IGRE rubric for logging scientific taste and
  high-tail research upside without pretending it is a complete reward model.
- `candidates.json`: candidate research directions and a scoring rubric.
- `experiment_protocol.md`: minimal benchmark and ablation plan.
- `prospective_matched_budget_protocol.md`: machine-checkable evidence shape
  required before strong top-conference claims about co-pilot superiority,
  human attention efficiency, or paper-quality gains.
- `paper_en.md`: English manuscript draft.
- `paper_zh.md`: Chinese manuscript draft.
- `references.bib`: citation seed file for later LaTeX/PDF generation.
- `RUNBOOK_EN.md`: English reproduction and continuation runbook.
- `RUNBOOK_ZH.md`: Chinese reproduction and continuation runbook.
- `audits/human_gate_attention_cost_audit.md`: coverage audit for whether gate
  logs contain measured human attention cost.
- `audits/taste_insight_coverage_audit.md`: coverage audit for whether gate
  logs contain complete scientific taste/insight records.
- `audits/top_conference_readiness_audit.md`: strict objective-level audit
  separating delivered artifacts from remaining top-conference evidence gaps.
- `audits/clean_clone_reproducibility_audit.md`: fresh GitHub-clone check that
  rebuilds PDFs, reruns gate audits, and verifies manifest artifact coverage.
- `audits/skill_reuse_smoke_audit.md`: local smoke test that instantiates the
  reusable Codex skill templates and validates a generated human gate log.
- `audits/attention_cost_logging_smoke_audit.md`: synthetic tooling smoke test
  for creating future human gate logs with complete attention-cost fields.
- `audits/attention_taste_logging_smoke_audit.md`: synthetic tooling smoke test
  showing that future prospective gates can jointly record complete
  attention-cost and scientific-taste fields.
- `audits/prospective_matched_budget_package_audit.md`: strict audit for
  whether a non-synthetic prospective matched-budget package exists.
- `audits/prospective_matched_package_summary.md`: metric-level summary of
  currently passing prospective packages, separating positive micro-task
  evidence from negative FML-bench evidence.
- `audits/fml_matched_comparison_summary.md`: machine-generated aggregate of
  archived FML matched-budget comparisons, separating the formal two-pair
  Causality replicate from the online smoke comparison.
- `experiments/prospective_matched_fml_causality_20260602_000001/paper_quality/`:
  matched mini-manuscript quality probe comparing the co-pilot package
  manuscript against an autonomous baseline manuscript.
- `experiments/full_gate_retrospective_trajectory.md`: auditable
  retrospective chain linking idea, evaluator, branch, program-search, and
  claim gates.
- `experiments/full_gate_executable_trace/`: output from a rerunnable
  full-gate trajectory runner that traverses archived experiment artifacts in
  one continuous gate sequence.
- `experiments/online_full_gate_smoke_20260601_145720/`: fresh online smoke
  trajectory that launched remote FML-bench and OpenEvolve work under the five
  proposed gates.
- `build/`: generated PDFs and other render outputs.

## Build PDFs

The local machine does not need LaTeX. Install the Python dependencies and run:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_copilot_v3_pdfs.py --language both
```

Expected outputs:

- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_en.pdf`
- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_zh.pdf`

## Current Status

This is a working research-production scaffold with preliminary Ubuntu-host
evidence. It includes OpenEvolve-based program search, direct LLM rewrite
baselines, richer knapsack and Max-Cut heuristic tasks, and retrospective branch-gate
replay over prior AI Scientist-v2/FML-bench runs. It now also includes live
two-draft FML-bench branch-gate probes, snapshot-seeded selected-branch
continuation runs, and two matched-budget four-step autonomous baselines on the
Causality task. The first pair weakly favors human-gated continuation on held
out test MAE (`0.402170` vs. `0.421474`), while the second pair favors the
autonomous baseline (`0.646224` vs. `0.595685`). The two-pair mean slightly
favors autonomous, so the manuscript now treats FML as mixed feasibility
evidence rather than a proof of human-gate superiority. This result is also
captured in the machine-generated `audits/fml_matched_comparison_summary.md`,
which adds win counts, mean delta, and SEM while explicitly marking the
statistical claim as unsupported because `n=2`. To avoid overfitting the
project to FML-bench, the package also includes a non-FML MLAgentBench
`vectorization` comparison: direct DeepSeek rewrite failed the correctness gate, while
three-iteration OpenEvolve-style search over eight random seeds retained a
correct best program in every seed and achieved median best runtime `0.024581`
seconds versus `3.261186` seconds for the controlled starter program. The result
is stronger than the earlier three-seed probe, but still seed-sensitive because
individual best runtimes range from `0.009210` to `2.984610` seconds. A second
controlled non-FML sklearn diabetes tabular regression probe starts from a
rudimentary mean predictor (`78.572189` RMSE); direct DeepSeek rewrite and three
OpenEvolve seeds all improve to roughly Ridge-level performance, with direct
editing matching the median OpenEvolve RMSE (`55.895460`). This adds a useful
boundary condition: program search should be gated, not automatic. A controlled
Max-Cut heuristic probe gives a second non-FML algorithmic subproblem for the
verifiable micro-evolution operator: a direct DeepSeek rewrite improved the starter from
`0.734680` to `0.962237`, while a five-iteration OpenEvolve run reached
`0.970833`. The margin is small and single-seed, so it supports selective
escalation rather than automatic program search. A first
online `Fairness_fairlearn` branch-gate extension was attempted and archived as
`fml_fairness_gated_drafts_failed/`; both drafts failed validation, so it is a
failure-mode/evaluator-gate artifact rather than performance evidence. A
follow-up Fairness evaluator-gate repair probe is archived in
`fml_fairness_evaluator_gate_repair.md`: the API-repaired branch runs but is
worse on the target fairness metric, while an all-negative predictor gets
perfect demographic parity by collapsing balanced accuracy to `0.500000`.
Claims remain intentionally conservative until the evidence is expanded across
more tasks and independently reviewed for paper quality. A Monica-routed claim
audit is archived under `audits/` and is reflected in the manuscript's
claim-audit section. A second paper-quality review pass through Monica-routed
`gpt-4o-mini` and `claude-3-7-sonnet-latest` is also archived; it now treats the
two matched-budget FML pairs as useful but mixed first evidence while still
identifying multi-task matched comparisons and a full four-loop trajectory as
the main blockers before a strong venue submission.

The package now includes a scientific taste and insight rubric. It records
non-metric human judgment as an auditable search prior: problem depth, novelty
potential, mechanistic value, failure informativeness, benchmark taste, claim
significance, and risk asymmetry. This keeps IGRE distinct from generic
co-pilot approval workflows. The rubric does not prove performance improvement
by itself; it lets future matched runs test whether human taste changes the
upper tail of research trajectories. A new coverage audit now covers 18 gate
records: 8 standalone human-gate logs and 10 embedded trajectory gates across 2
trajectory artifacts. It finds 1 complete `taste_insight` record, the
scientific-taste prior that captures the author's benchmark-portfolio and
high-tail framing decision, and 17 older gates without taste/insight fields.
This is an initial logging artifact, not performance evidence: future
prospective gates must record the field before the paper can argue that
taste-gated search changed research outcomes.

The latest benchmark-expansion probes are deliberately recorded as setup
evidence rather than inflated results. A second official MLAgentBench
`debug`/CIFAR10 attempt repaired the missing `torchvision` dependency but was
stopped when the 170 MB CIFAR10 archive downloaded at only a few hundred KB over
half a minute. An additional MLAgentBench `imdb` attempt repaired the missing
`datasets` dependency, but the Ubuntu host could not reach HuggingFace to load
even a five-example split. A ScienceAgentBench metadata probe confirmed the code repository
and the April 2026 verified-artifact requirement, but HuggingFace metadata was
not reachable from the Ubuntu host. Neither probe is reported as a benchmark
score.

The package now also includes a retrospective full-gate trajectory. It links
the selected research direction, Fairness evaluator guardrail, live Causality
branch gate, OpenEvolve program-search escalation, and claim-audit decision into
one auditable chain. This is evidence that the schema covers all proposed human
gate types, but it is not yet a single online end-to-end co-pilot run.

Following the latest paper-quality review, the schema and template now include
an `attention_cost` block for active review minutes, wall-clock latency, options
reviewed, artifacts reviewed, and decision count. The current attention-cost
audit covers 18 gate records: 8 standalone archived gate logs and 10 embedded
trajectory gates across 2 trajectory artifacts. It finds zero complete measured
attention-cost records. This is treated as a measurement-readiness gap: the
logs support decision provenance, but not yet any claim that gates improve
research quality per unit of human effort.

The latest addition is an executable full-gate trace runner:
`scripts/run_full_gate_trajectory.py`. The runner reads the current archived
experiment summaries and emits
`experiments/full_gate_executable_trace/trajectory.json` plus a Markdown
summary. This is stronger than a hand-written retrospective chain because the
gate decisions are recomputed from artifact files, but it is still explicitly
marked as `executable_artifact_replay`, not as a fresh online training run.

The package now also contains a first fresh online full-gate smoke trajectory,
generated by `scripts/run_online_full_gate_smoke.py`. On `ubuntu-heshi`, it ran
a new two-draft FML-bench Causality frontier, selected step 2 by validation MAE
(`0.627837` versus `0.677448`), continued the selected snapshot for one step,
and ran a one-iteration OpenEvolve knapsack search in the same trajectory. The
continuation test MAE was `0.862015`, worse than the selected frontier's test
MAE `0.646224`, so this artifact supports online orchestration feasibility
rather than performance improvement.

A same-FML-step autonomous baseline was then run for the online smoke. It used
the same Causality task and DeepSeek model for three AI Scientist-v2 steps with
no human branch gate. The autonomous baseline reached validation MAE `0.354147`
and test MAE `0.428516`, outperforming the human-gated continuation on held-out
test MAE. The matched smoke comparison is archived as
`experiments/online_smoke_matched_autonomous_comparison.md` and is treated as a
negative performance result.

The latest measurement-readiness addition is a prospective matched-budget
package protocol and audit. The validator
`scripts/audit_prospective_matched_budget_package.py` requires a single
non-synthetic package to contain a prospective co-pilot trajectory, a matched
autonomous baseline, complete `attention_cost` and `taste_insight` records for
every human gate, a claim audit, and a manuscript produced from the same run.
The repository now contains one passing controlled micro-pilot package under
`experiments/prospective_matched_micro_pilot_20260602_000001/`. It ran a real
weighted Max-Cut micro-task on `ubuntu-heshi`, but it is still only
evidence-shape validation: it does not use AI Scientist-v2 tree search and does
not support paper-quality or co-pilot-superiority claims.

The repository also now contains a stronger FML-bench prospective matched
package under `experiments/prospective_matched_fml_causality_20260602_000001/`.
It ran fresh `Causality_causalml` co-pilot and autonomous runs on `ubuntu-heshi`
with the same DeepSeek model and two-step budget, complete attention/taste gate
logging, claim audit, and same-run manuscript. The result is negative for
co-pilot performance in this small run: co-pilot test MAE is `0.646224`, while
the autonomous matched baseline reaches `0.624703` (lower is better). This is
useful evidence because it upgrades the package shape to AI Scientist-v2-style
FML-bench while still keeping the paper's superiority claim unproven.

The metric-level package summary is archived as
`audits/prospective_matched_package_summary.md`. It currently summarizes 2
passing packages: 1 controlled micro-task win for a human-selected branch and 1
FML-bench loss for the co-pilot branch. Both packages have complete
`attention_cost` and `taste_insight` gate records. This mixed result is the
intended evidence discipline for IGRE: human taste/insight is treated as a
high-variance search intervention to be measured, not as an assumed positive
effect.

The package now includes a first matched mini-manuscript quality probe under
`experiments/prospective_matched_fml_causality_20260602_000001/paper_quality/`.
The probe generates an autonomous baseline mini-manuscript from the same
package evidence and asks Monica-routed `gpt-4o-mini` and
`claude-3-7-sonnet-latest` to score anonymized manuscripts A/B. Both reviewers
prefer the co-pilot package mini-manuscript (`overall 4` versus `3`), mainly
because it is better calibrated and more explicit about limitations. This is
useful measurement-readiness evidence, but it is not a full paper-quality
result: the artifacts are short package manuscripts from one FML task, not
complete end-to-end generated papers.
