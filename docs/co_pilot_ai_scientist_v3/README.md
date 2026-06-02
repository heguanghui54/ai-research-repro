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
- `experiments/hypothesis_frontier_smoke_20260602_021500/`: live
  Monica-routed AI Co-Scientist-style generate-critique-rank smoke over four
  new research-frontier candidates.
- `prospective_matched_budget_protocol.md`: machine-checkable evidence shape
  required before strong top-conference claims about co-pilot superiority,
  human attention efficiency, or paper-quality gains.
- `paper_en.md`: English manuscript draft.
- `paper_zh.md`: Chinese manuscript draft.
- `paper_en_focused.md`: focused conference-style English main-paper draft.
- `paper_zh_focused.md`: focused conference-style Chinese main-paper draft.
- `references.bib`: citation seed file for later LaTeX/PDF generation.
- `RUNBOOK_EN.md`: English reproduction and continuation runbook.
- `RUNBOOK_ZH.md`: Chinese reproduction and continuation runbook.
- `audits/human_gate_attention_cost_audit.md`: coverage audit for whether gate
  logs contain measured human attention cost.
- `audits/taste_insight_coverage_audit.md`: coverage audit for whether gate
  logs contain complete scientific taste/insight records.
- `audits/top_conference_readiness_audit.md`: strict objective-level audit
  separating delivered artifacts from remaining top-conference evidence gaps.
- `focused_submission_rewrite_plan.md`: conference-style rewrite plan that
  separates the current lab-record manuscript from the focused main paper
  needed for a strong venue.
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
python3 scripts/build_copilot_v3_pdfs.py --language both --variant focused
```

Expected outputs:

- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_en.pdf`
- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_zh.pdf`
- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_focused_en.pdf`
- `docs/co_pilot_ai_scientist_v3/build/co_pilot_ai_scientist_v3_focused_zh.pdf`

## Current Status

This is a working research-production scaffold with preliminary Ubuntu-host
evidence. The current paper should be read primarily as a human-participation
workflow design study for automated science: the goal is to compare and refine
participation modes that make human scientific taste and insight usable inside
AI Scientist-v2-style loops, not to claim that human participation already
improves every paper-quality or benchmark metric. It now includes a live AI
Co-Scientist-style hypothesis-frontier
smoke: two Monica-routed `gpt-4o-mini` calls generated four candidate research
frontiers, critiqued/ranked them, and selected `frontier_004` (structured human
feedback mechanisms) as the next-budget candidate. This supports front-end
orchestration only. The same archived IGRE frontier portfolio is now compared
against an autonomous AI Scientist-v2-style hypothesis front end in
`experiments/hypothesis_frontend_baseline_20260602_030500/`: two additional
Monica-routed `gpt-4o-mini` calls generated a no-human-taste autonomous
portfolio and scored the two portfolios. The scorer preferred the IGRE
portfolio (`overall 4` vs. `3`) because of stronger evidence gain, benchmark
fit, claim calibration, and human-taste visibility, while noting that the
autonomous portfolio is stronger for exploring fully autonomous process
variants. This is direction-finding evidence only, not downstream benchmark or
paper-quality evidence. The selected frontier is also connected to a same-manuscript
structured-feedback probe in
`experiments/structured_feedback_probe_20260602_022900/`: five Monica-routed
`gpt-4o-mini` calls generated informal feedback, IGRE-structured feedback, two
revisions of the same base manuscript, and a fixed-rubric model score. The
scorer preferred the structured revision (`overall 5` vs. `4`) on clarity,
claim calibration, evidence grounding, and method distinctness. This is
measurement-readiness evidence, not independent human expert review or a
general paper-quality result.
Finally, `experiments/expert_review_taste_prior_probe_20260602_031800/` uses
the Hugging Face `nhop/OpenReview` dataset through streaming access as an
offline expert-review proxy for scientific taste. The probe verifies 34,638
dataset rows, samples 160 rows without downloading the full dataset, and finds
usable score fields for overall score, novelty, correctness, clarity, impact,
and confidence, while noting that reproducibility scores are absent in the
sample. This can support a limited offline taste-prior experiment; it is not
live human co-pilot interaction data. Its most useful role is as a
participation-mode selection benchmark: compare hypotheses, plans, evidence
summaries, or manuscript revisions produced by different gate patterns against
the same expert-review proxy before deciding which human-in-the-loop workflow
is strongest. Four new probes now exercise that idea. The
`participation_mode_selection_probe_20260602_060500/` artifact compares
no-gate, taste-prior, evaluator-stress, structured-feedback, and
claim-calibration modes under an OpenReview-conditioned model scorer; it places
structured-feedback and claim-calibration as the current top pair. The
`openreview_guided_regeneration_probe_20260602_073500/` artifact expands the
regeneration test to six ML/AI OpenReview papers and regenerates mini-paper
artifacts with and without real review snippets; the review-guided versions win
in `5/6` pairs, increasing mean overall score from `3.0` to `3.8333`. The one
baseline win is retained as evidence that review text is useful only when it
can be converted into clearer problem framing, experiments, limitations, or
claim calibration. The
`openreview_regeneration_cross_model_review_20260602_081500/` artifact then
re-scores the same six generated pairs with Monica-routed
`claude-3-7-sonnet-latest`; this stricter cross-model review gives
review-guided `3/6` wins, baseline `1/6` win, and `2` ties, with a smaller
mean delta of `+0.1667`. This makes the claim more conservative: review text is
an actionable workflow signal, not an automatic quality booster. The
`review_insight_taxonomy_probe_20260602_064500/` artifact mines 32 review cases
and maps actionable review patterns to IGRE gates: novelty concerns to
scientific taste prior, limitations/weaknesses to claim calibration, clarity
issues to structured feedback, and metric/evaluation issues to evaluator stress
testing. The `review_utility_map_probe_20260602_071500/` artifact then applies
a deterministic utility map to 473 review snippets from the same 160-paper
sample. It finds 398 snippets with actionable gate signals and 64 with noisy
low-actionability signals; evaluator-stress, structured-feedback, claim
calibration, and scientific-taste-prior gates receive 245, 210, 140, and 111
actionable triggers respectively. This supports the workflow claim that useful
human taste/insight is the subset of review feedback that can alter search
direction, evaluator design, manuscript structure, or claim boundaries.
The package also includes OpenEvolve-based program search, direct LLM rewrite
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
upper tail of research trajectories. The derived Human Co-Pilot Trace Dataset
protocol now indexes 52 gate records from the real Codex project workflow, with
35 records containing attention-cost fields and 10 containing taste/insight
fields. The strict gate audits are narrower: they currently cover 39 gate
records and find 1 complete attention-cost record plus 2 complete taste/insight
records. It is still a single-author longitudinal case study, not
population-level human-subjects evidence.

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
audit covers 39 gate records: 9 standalone archived gate logs and 30 embedded
trajectory gates across 6 trajectory artifacts. It finds 1 complete
operator-recorded attention-cost event and 38 incomplete records. This is
treated as measurement-readiness evidence: the logs support decision provenance
and the complete logging path now works, but they do not yet support any claim
that gates improve research quality per unit of human effort.

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

The package now also includes a repeated same-run online paired-smoke summary
generated by `scripts/summarize_online_paired_smokes.py`. Across three
same-continuous online smokes with autonomous baselines, two Causality runs
have valid scalar metrics and one `Fairness_fairlearn` run is a no-valid-branch
failure trajectory. The valid Causality aggregate is `0` co-pilot wins, `1`
autonomous win, and `1` tie; mean test MAE is `0.754120` for co-pilot and
`0.643337` for autonomous. Monica-routed model reviewers prefer the co-pilot
manuscripts in `6/6` reviewer calls, which is recorded only as
manuscript-measurement readiness, not independent expert review.

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

A second prospective FML package is archived under
`experiments/prospective_matched_fml_causality_20260602_010002/`. It uses the
same task/model/tool budget shape and is also negative for co-pilot performance:
co-pilot test MAE is `0.646224`, while the matched autonomous baseline reaches
`0.296399`.

A third FML package is archived under
`experiments/prospective_matched_fml_fairness-fairlearn_20260602_002821/`.
It expands the prospective package protocol beyond Causality into the available
Fairness workspace on `ubuntu-heshi`. In this run the co-pilot branch frontier
produced no valid scored continuation, so the logged gate chooses
`abort_no_valid_branch`; the matched autonomous run produced test primary metric
`0.172152` (`abs_demographic_parity_diff_mean`, lower is better). This is a
negative result and a useful evaluator-gate failure case, not evidence of
co-pilot superiority.

The metric-level package summary is archived as
`audits/prospective_matched_package_summary.md`. It currently summarizes 4
passing packages: 1 controlled micro-task win for a human-selected branch and 3
FML-bench losses or invalid-continuation cases for the co-pilot branch. All four packages have complete
`attention_cost` and `taste_insight` gate records. This result is the intended
evidence discipline for IGRE: human taste/insight is treated as a high-variance
search intervention to be measured, not as an assumed positive effect.

The repository also includes `human_copilot_trace_dataset.md/json`, which
answers the data question directly. Public human-AI datasets such as CoAuthor,
CUPID, broad agent trajectory collections, and WebChain are useful related
resources, but they do not directly provide human scientist co-pilot
interventions inside an AI Scientist-v2-style hypothesis-experiment-paper loop.
The paper therefore uses a privacy-preserving derived metadata layer from the
author's own Codex sessions as its primary process trace dataset.
`audits/human_copilot_trace_dataset_audit.md/json` checks this release layer:
the current audit passes with 0 secret-pattern hits and 0 raw-log marker hits,
so the dataset is suitable as a derived single-author case-study artifact.

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

The latest manuscript-readiness probe is archived under
`experiments/prospective_matched_fml_fairness-fairlearn_20260602_002821/full_manuscript_probe/`.
It deterministically renders the same archived FML evidence into two complete
paper-shaped manuscripts and scores them with an internal rubric. The co-pilot
manuscript scores `4.18` overall and the autonomous manuscript scores `4.11`,
while the autonomous baseline is the only path with a valid scalar FML test
metric. This narrows the manuscript-generation gap but is still not a fresh
online end-to-end trajectory or independent expert paper-quality result.

The newest online manuscript-production smoke is archived under
`experiments/online_full_gate_smoke_20260602_010521/`. It reruns a fresh online
five-gate trajectory on `ubuntu-heshi`, launches a same-run autonomous
AI Scientist-v2 baseline, and renders the logged trajectory into paired
manuscripts under `online_manuscript/`. The co-pilot path selected branch
`step_0001` with validation MAE `0.621461`, reached continuation test MAE
`0.862015`, and produced a one-iteration knapsack program-search score
`0.994177`. The same-run autonomous baseline reached test MAE `0.640451`.
The generated co-pilot manuscript scores `4.64` on the internal trace-bound
rubric, while the autonomous comparator manuscript scores `3.48`. This closes
the narrow same-continuous-trajectory manuscript-comparator gap for a smoke
setting, and the repeated summary now covers three paired runs, including one
Fairness failure-mode trajectory. It remains a tiny-budget benchmark-negative,
tied, or no-valid result without independent paper-quality review.
