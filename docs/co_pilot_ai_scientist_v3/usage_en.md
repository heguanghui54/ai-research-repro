# Co-Pilot AI Scientist v3 Usage Guide

## What This Workflow Does

This workflow turns a research topic into a human-guided automated research
loop. It keeps AI Scientist-v2-style automation, but adds explicit human gates
where expert judgment is most valuable.

## Minimal Run Plan

1. Start from `problem_statement.md`.
2. Generate candidate hypotheses and store them in `candidates.json`.
3. Ask the human researcher to approve or edit the best hypothesis.
4. Convert the approved hypothesis into benchmarks and evaluators.
5. Run autonomous and human-gated variants under the same budget.
6. Send machine-gradeable subproblems to OpenEvolve or another code-evolution
   loop.
7. Write the paper from logs and metrics only.
8. Run a final claim audit before producing PDFs.
9. Run a paper-quality review pass and revise unsupported top-conference claims.

The current package includes an example claim audit under
`docs/co_pilot_ai_scientist_v3/audits/`. Use it as the model for future runs:
claims must be marked as supported, partially supported, unsupported, or
overstated before the final PDF build.

To regenerate the current executable gate-chain replay, run:

```bash
python3 scripts/run_full_gate_trajectory.py
```

This writes `experiments/full_gate_executable_trace/trajectory.json` and
`README.md`. Treat it as a reproducibility check over archived artifacts, not
as a fresh online full-gate experiment.

To launch a small fresh online full-gate smoke trajectory on `ubuntu-heshi`,
run:

```bash
python3 scripts/run_online_full_gate_smoke.py \
  --branch-steps 2 \
  --continuation-steps 1 \
  --program-iterations 1 \
  --run-autonomous-baseline \
  --autonomous-steps 3
```

This runs FML-bench, OpenEvolve, and a same-run autonomous AI Scientist-v2
baseline remotely. It is intended to prove orchestration feasibility and create
a paired smoke comparison; it is still too small for any general performance
claim.

The archived smoke has a matched autonomous comparison in
`experiments/online_smoke_matched_autonomous_comparison.md`. The autonomous
baseline wins on held-out test MAE, so use it as a negative-result template.

For a Monica-routed AI Co-Scientist-style hypothesis-frontier smoke, source the
global environment and run:

```bash
source ~/.codex/env
python3 scripts/run_hypothesis_frontier_smoke.py \
  --model gpt-4o-mini
```

This generates candidate research frontiers and a critique/ranking artifact.
Treat it as front-end orchestration evidence, not as benchmark or paper-quality
evidence.

To compare that IGRE front end against a same-model autonomous AI
Scientist-v2-style hypothesis front end, run:

```bash
source ~/.codex/env
python3 scripts/run_hypothesis_frontend_baseline.py \
  --model gpt-4o-mini
```

This is a front-end portfolio comparison only. It does not evaluate downstream
benchmark performance, paper quality, or human expert judgment.

To connect the selected structured-feedback frontier to a downstream
same-manuscript measurement probe, run:

```bash
source ~/.codex/env
python3 scripts/run_structured_feedback_probe.py \
  --model gpt-4o-mini
```

This generates informal feedback, IGRE-structured feedback, two revisions of
the same base manuscript, and a fixed-rubric model score. Treat the output as
measurement-readiness evidence only; it is not independent human peer review.

To probe Hugging Face/OpenReview expert-review data as an offline scientific
taste prior without downloading the full dataset, run:

```bash
python3 scripts/run_expert_review_taste_prior_probe.py \
  --streaming \
  --stream-limit 160
```

The current probe uses `nhop/OpenReview`, verifies Dataset Viewer metadata, and
streams a small sample. Treat this as an offline expert-review proxy for
scientific taste, not as live human co-pilot interaction data. The intended
experiment is to use the same OpenReview-derived rubric to compare artifacts
from different participation modes, such as no gate, taste-prior gate,
evaluator-stress gate, structured-feedback gate, and claim-calibration gate.

To run that participation-mode comparison directly, use:

```bash
source ~/.codex/env
python3 scripts/run_participation_mode_selection_probe.py \
  --model gpt-4o-mini
```

To test whether real review comments improve regenerated ML/AI mini-paper
artifacts, run:

```bash
source ~/.codex/env
python3 scripts/run_openreview_guided_regeneration_probe.py \
  --model gpt-4o-mini \
  --indices 1,34,49
```

To evaluate whether historical reviews would have steered the workflow toward
later field trajectories, use Temporal Frontier Replay (TFR). The current
archived package already contains the deterministic smoke, citation-backed
probe, review-frontier signal probe, and semantic judge probe; to audit that
package without new model calls, run:

```bash
python3 scripts/audit_temporal_frontier_replay.py
```

To rerun the full TFR probe chain, use:

```bash
python3 scripts/run_retrospective_frontier_alignment_smoke.py
python3 scripts/run_retrospective_frontier_citation_probe.py
python3 scripts/run_review_frontier_signal_probe.py

source ~/.codex/env
python3 scripts/run_semantic_frontier_judge_probe.py \
  --model gpt-4o-mini

python3 scripts/audit_temporal_frontier_replay.py
```

For the long-horizon human-taste question, use LHTG/DVRS as the routing layer
around TFR. LHTG is not a sixth ordinary gate; it is the rule that decides which
human reviews deserve delayed-value replay because they may look costly in the
short term while pointing toward later mainstream or SOTA directions.

To screen and validate delayed-value review candidates, run:

```bash
python3 scripts/run_delayed_value_review_candidate_mining.py
python3 scripts/run_delayed_value_candidate_frontier_validation.py
python3 scripts/audit_long_horizon_taste_gate.py
python3 scripts/audit_top_conference_evidence_roadmap.py
```

Interpret this audit conservatively. The current archived package finds `120`
delayed-value replay candidates and a small delayed-candidate-vs-control
frontier advantage, but `0` positive delayed-value cases. This supports replay
prioritization and a falsifiable protocol, not a claim that human reviews have
already improved long-horizon discovery.

TFR should be interpreted strictly. A positive delayed-value case requires
review guidance to reduce short-term quality while increasing later-frontier
alignment beyond both paper-only and shuffled-review-control conditions. The
current archived audit is negative for delayed-value evidence, which is a
measurement boundary rather than a failure of the protocol.

The roadmap audit checks that the current top-conference blockers are converted
into concrete next experiments. Passing it means the roadmap is actionable; it
does not mean the independent human-review or matched-benchmark milestones have
already been completed.

To mine which review comments are actionable as scientific taste/insight for
IGRE gates, run:

```bash
source ~/.codex/env
python3 scripts/run_review_insight_taxonomy_probe.py \
  --model gpt-4o-mini \
  --review-limit 32
```

To build a deterministic utility map from a larger OpenReview sample without
additional model calls, run:

```bash
python3 scripts/run_review_utility_map_probe.py
```

This maps review snippets to actionable gate controls and separates useful
signals such as evaluation concerns, claim-boundary issues, novelty
positioning, reproducibility details, and concrete suggestions from generic
praise or vague reactions.

For a Monica-routed paper-quality review, source the global environment and run:

```bash
source ~/.codex/env
python3 scripts/run_paper_quality_review.py \
  --models gpt-4o-mini claude-3-7-sonnet-latest \
  --max-tokens 4096
```

Treat the output as review evidence, not as proof of acceptance.

To audit whether human gates contain measured attention cost, run:

```bash
python3 scripts/audit_human_gate_attention_cost.py
```

For future matched-budget experiments, every prospective gate log should fill
`attention_cost.active_review_minutes`,
`attention_cost.wall_clock_latency_minutes`, `options_reviewed`,
`artifacts_reviewed_count`, and `decision_count`. Retrospective estimates should
be marked as missing rather than guessed.

To build the privacy-preserving derived Human Co-Pilot Trace Dataset from the
current repository artifacts, run:

```bash
python3 scripts/build_human_copilot_trace_dataset.py
```

This writes `human_copilot_trace_dataset.md/json`. It indexes gate records,
commits, prospective packages, and artifact links. It deliberately avoids
publishing raw Codex chat logs or credentials, so treat it as a single-author
longitudinal process dataset rather than population-level human-subject data.
Before release, audit the derived dataset:

```bash
python3 scripts/audit_human_copilot_trace_dataset.py
```

The current audit writes `audits/human_copilot_trace_dataset_audit.md/json` and
passes with zero secret-pattern hits and zero raw-log marker hits.

To create a schema-compatible prospective gate log with measured attention
cost and scientific taste/insight, use:

```bash
python3 scripts/create_human_gate_log.py \
  --gate-id frontier_gate_live_001 \
  --gate-type frontier_steering \
  --research-task-id your_task_id \
  --option 'branch_a::Continue branch A' \
  --option 'branch_b::Stop branch B' \
  --human-decision branch_a \
  --rationale 'Human rationale here.' \
  --prompted-at-utc 2026-06-01T18:00:00Z \
  --decision-at-utc 2026-06-01T18:04:30Z \
  --active-review-minutes 3.5 \
  --artifacts-reviewed-count 1 \
  --taste-score problem_depth=5 \
  --taste-score novelty_potential=4 \
  --taste-score mechanistic_value=4 \
  --taste-score failure_informativeness=5 \
  --taste-score benchmark_taste=5 \
  --taste-score claim_significance=4 \
  --taste-score risk_asymmetry=4 \
  --taste-insight-score 4.43 \
  --taste-rationale 'Why this changes the search frontier.' \
  --non-metric-factor 'high-tail-research-upside' \
  --require-complete-attention \
  --require-complete-taste \
  --output docs/co_pilot_ai_scientist_v3/human_gate_logs/frontier_gate_live_001.json
```

To record scientific taste and insight, use:

```text
docs/co_pilot_ai_scientist_v3/taste_insight_rubric.md
```

Fill the optional `taste_insight` block in prospective gate logs when a human
decision changes the search frontier for non-metric reasons such as novelty,
failure value, benchmark taste, or risk asymmetry. Do not treat this score as a
reward model; report it as an auditable search prior and compare downstream
outcomes against autonomous baselines.

To audit whether the archived gates contain complete taste/insight records,
run:

```bash
python3 scripts/audit_taste_insight_coverage.py
```

The current strict archive audit has 2 complete taste/insight records: the
author's benchmark-portfolio/high-tail framing decision and an operator-recorded
decision to prioritize attention/taste measurement before stronger human
efficiency claims. It also has 1 complete attention-cost record. Treat these as
logging and measurement-readiness evidence, not as performance evidence about
human scientific taste.

To check whether the repository contains a qualifying prospective matched-budget
package, run:

```bash
python3 scripts/audit_prospective_matched_budget_package.py
```

This audit is the hard gate before stronger claims. It passes only when a
non-synthetic package contains a prospective co-pilot trajectory, a matched
autonomous baseline, complete `attention_cost` and `taste_insight` records for
all human gates, a claim audit, and a manuscript from the same run.

To summarize the measured outcomes of the passing packages, run:

```bash
python3 scripts/summarize_prospective_matched_packages.py
```

This writes `audits/prospective_matched_package_summary.md/json`. Use it to
separate evidence-shape success from actual benchmark outcomes. The current
summary contains one controlled micro-task co-pilot win and one FML-bench
co-pilot loss.

To regenerate the aggregate FML matched-comparison table, run:

```bash
python3 scripts/summarize_fml_matched_comparisons.py
```

This writes `audits/fml_matched_comparison_summary.md/json`. It keeps the formal
two-pair Causality replicate separate from the online smoke comparison.

To score the current matched FML mini-manuscripts, run:

```bash
python3 scripts/score_matched_manuscripts.py
```

This generates an autonomous mini-manuscript for the package and writes
`experiments/prospective_matched_fml_causality_20260602_000001/paper_quality/summary.md`.
Treat this as a narrow manuscript-quality probe, not a full paper-quality claim.

To regenerate the deterministic full-manuscript generation probe, run:

```bash
python3 scripts/generate_full_manuscript_probe.py --update-manifest
python3 scripts/generate_full_manuscript_probe.py \
  --package-dir docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_fml_fairness-fairlearn_20260602_002821 \
  --update-manifest
```

This writes two complete paper-shaped manuscripts and
`full_manuscript_probe/summary.md` under the selected package. The latest
Fairness package probe scores co-pilot `4.18` and autonomous `4.11` on the
internal rubric, while autonomous is the only path with a valid scalar FML test
metric.
It is an archived-evidence manuscript probe, not a fresh end-to-end research
trajectory or independent expert review.

To generate a manuscript from an online full-gate trajectory, run:

```bash
python3 scripts/generate_online_trajectory_manuscript.py \
  --trajectory-json docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/trajectory.json \
  --autonomous-summary-json docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/autonomous_baseline_summary.json \
  --update-manifest
```

The archived `online_full_gate_smoke_20260602_010521` run is a fresh online
smoke trajectory with a same-run autonomous baseline. Passing
`--autonomous-summary-json` writes
`online_manuscript/autonomous_online_comparator_manuscript.md` and
`online_manuscript/matched_budget_comparison_summary.md`.

To run the Monica-routed A/B model-review probe on those paired manuscripts,
run:

```bash
set -a; . ~/.codex/env; set +a
python3 scripts/score_matched_manuscripts.py \
  --co-pilot-manuscript docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/online_manuscript/co_pilot_online_full_gate_manuscript.md \
  --autonomous-manuscript docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/online_manuscript/autonomous_online_comparator_manuscript.md \
  --output-dir docs/co_pilot_ai_scientist_v3/experiments/online_full_gate_smoke_20260602_010521/online_manuscript/paper_quality \
  --probe-id online_full_gate_smoke_20260602_010521_same_continuous \
  --probe-kind full-manuscripts
```

Treat the output as model-review measurement evidence, not expert peer review.

To summarize all archived same-run paired online smokes, run:

```bash
python3 scripts/summarize_online_paired_smokes.py --update-manifest
```

The current repeated-smoke summary reports `3` paired online runs: two valid
Causality metric comparisons with `0` co-pilot benchmark wins, `1` autonomous
win, and `1` tie, plus one Fairness no-valid failure trajectory. It should be
cited as orchestration and manuscript-measurement readiness evidence, not as
co-pilot benchmark superiority.

To regenerate the controlled micro-pilot package shape on `ubuntu-heshi`, run:

```bash
python3 scripts/run_prospective_matched_budget_micro_pilot.py \
  --host ubuntu-heshi
python3 scripts/audit_prospective_matched_budget_package.py
```

This is useful for validating the package format, but it is not a substitute
for an AI Scientist-v2/FML or MLAgentBench prospective matched-budget run.

To run the smallest current FML-bench prospective matched package, use:

```bash
python3 scripts/run_prospective_fml_matched_package.py \
  --host ubuntu-heshi \
  --task-config configs/tasks/causality_causalml.yaml \
  --benchmark-slug causality-causalml \
  --max-steps 2
python3 scripts/audit_prospective_matched_budget_package.py
```

Use `--task-config configs/tasks/fairness_fairlearn.yaml --benchmark-slug
fairness-fairlearn` for the currently available Fairness workspace. The archived
FML packages are negative results or invalid-continuation cases for co-pilot
performance at this budget, so treat them as pilot evidence and templates for
larger runs.

## Human Gate Types

- `scientific_taste_prior`: choose or rewrite the research hypothesis using
  scientific taste and upside, not only current scores.
- `long_horizon_taste_gate`: route reviews or human interventions into
  delayed-value replay when they may reduce short-term quality but point toward
  later field trajectories.
- `evaluator_stress_test`: approve metrics, baselines, and anti-gaming failure
  conditions.
- `frontier_steering`: choose which experiment branches receive more budget,
  including high-upside non-best branches.
- `verifiable_micro_evolution`: decide whether a subproblem deserves deeper
  code evolution.
- `claim_calibration`: remove, weaken, or reframe unsupported paper claims.

## Environment

Use API keys from global environment variables. Suggested routing:

- DeepSeek for low-cost coding and smoke runs.
- Monica-routed GPT/Gemini/Anthropic models for hypothesis debate, high-stakes
  review, and final writing.
- Ubuntu SSH host for heavier benchmark execution.

## Benchmark Choice

Do not default to FML-bench for every claim. Use benchmarks by claim type:

- FML-bench for AI Scientist-v2-style branch gates and continuation.
- OpenEvolve-controlled tasks, currently including function minimization,
  knapsack, and Max-Cut, for machine-gradeable algorithm search.
- MLAgentBench for non-FML ML experimentation and correctness-gated code
  optimization.
- Controlled sklearn tabular probes for cheap non-FML modeling evidence and
  escalation-boundary tests when external benchmark credentials are unavailable.
- ScienceAgentBench for data-driven scientific discovery only after the
  verified benchmark artifacts are downloaded on the Ubuntu host.
- PaperBench-style rubrics for claim and manuscript-quality audits when a full
  PaperBench run is too expensive.

## OpenEvolve Subproblem Search

Use OpenEvolve as the open-source substitute for AlphaEvolve-style optimization.
The official AlphaEvolve system is not available, so claims should say
"AlphaEvolve-style" or "OpenEvolve-based" unless official code is actually used.

Minimal OpenEvolve command using the repository wrapper:

```bash
python3 scripts/run_openevolve_program_search.py \
  --initial-program docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/initial_program.py \
  --evaluator docs/co_pilot_ai_scientist_v3/experiments/knapsack_task/evaluator.py \
  --output-dir /tmp/knapsack_openevolve_5iter/run \
  --iterations 5 \
  --provider deepseek \
  --model deepseek-chat
```

For Monica routing, use `--provider monica --model <model-name>` and make sure
`MONICA_API_KEY` and `MONICA_BASE_URL` are available in the shell.

See `RUNBOOK_EN.md` for the full reproduction path.
