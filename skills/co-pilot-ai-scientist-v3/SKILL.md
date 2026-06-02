---
name: co-pilot-ai-scientist-v3
description: Insight-Gated Research Evolution workflow for collaborative automated science, using human scientific taste, evaluator stress tests, frontier steering, verifiable micro-evolution, and claim calibration.
---

# Co-Pilot AI Scientist v3

## Purpose

Run collaborative automated research using Insight-Gated Research Evolution
(IGRE): machines maintain broad executable search frontiers, while human
scientists intervene as explicit high-variance operators where taste, insight,
and claim responsibility can reshape the trajectory.

The purpose is to design and compare useful human-participation patterns, not
to assume that human involvement always improves average benchmark or paper
quality. Treat each gate as a workflow-design choice that must be supported by
matched evidence and clear boundary conditions.

## Use This Skill When

- A user wants to turn a broad research idea into a paper with human guidance.
- A project needs hypothesis generation, benchmark execution, paper writing,
  and code-evolution subproblem search organized as one co-pilot method rather
  than a loose combination of prior systems.
- The user wants a co-pilot workflow rather than a fully autonomous pipeline.
- Human feedback must be logged as part of the reproducibility record.
- The evaluation should consider both mean benchmark performance and the chance
  of rare high-novelty, high-impact research outcomes.
- Historical peer-review data should be used as an offline proxy for human
  scientific taste, including tests of whether a review could have steered a
  project toward later field trajectories.

## Core Workflow

1. **Frame**
   - Convert the topic into a testable research question.
   - Define success metrics, failure conditions, and target venue level.

2. **Set Scientific Taste Prior**
   - Use multiple agents or model passes to generate, critique, and refine
     hypotheses.
   - For a live AI Co-Scientist-style front-end smoke, run
     `scripts/run_hypothesis_frontier_smoke.py` after sourcing the private model
     environment. Treat the generated frontier and critique/ranking as
     orchestration evidence, not as a downstream performance result.
   - To compare the IGRE hypothesis front end with a same-model autonomous
     AI Scientist-v2-style front end, run
     `scripts/run_hypothesis_frontend_baseline.py`. Treat this as front-end
     portfolio evidence only, not as paper-quality or benchmark evidence.
   - If the selected frontier concerns structured human feedback, run
     `scripts/run_structured_feedback_probe.py` to compare informal feedback
     with IGRE-structured feedback on the same base manuscript. Treat the score
     as measurement-readiness evidence, not as independent peer review.
   - To use public expert-review data as an offline scientific-taste proxy,
     run `scripts/run_expert_review_taste_prior_probe.py --streaming`. This
     can support a limited OpenReview-derived taste prior, but it is not live
     human co-pilot interaction data.
   - Use the OpenReview-derived proxy as a participation-mode selection
     benchmark: compare artifacts produced by no-gate, taste-prior,
     evaluator-stress, structured-feedback, and claim-calibration modes against
     the same expert-review rubric before deciding which workflow pattern is
     stronger.
   - Run `scripts/run_participation_mode_selection_probe.py` to compare those
     gate patterns directly under the OpenReview-conditioned scorer.
   - Run `scripts/run_openreview_guided_regeneration_probe.py` when you want to
     test whether real review snippets improve regenerated ML/AI mini-paper
     artifacts compared with title/abstract-only baselines.
   - Run `scripts/run_review_insight_taxonomy_probe.py` to mine which kinds of
     review comments are actionable for each IGRE gate. Treat the resulting
     taxonomy as workflow-design guidance, not as causal proof.
   - Run `scripts/run_review_utility_map_probe.py` to deterministically map a
     larger OpenReview sample into actionable and noisy review categories. Use
     this when deciding which human review signals should become gate controls:
     evaluation/metric and correctness concerns route to evaluator stress
     tests, claim-boundary concerns route to claim calibration, novelty/
     positioning signals route to scientific taste priors, and clarity/
     reproducibility/actionable suggestions route to structured feedback.
   - Use Temporal Frontier Replay (TFR) when the question is not immediate
     paper quality but long-horizon scientific direction. TFR replays a
     historical paper at time `t` under paper-only, review-guided, and
     shuffled-review-control conditions, then compares the generated artifacts
     with later field evidence at `t + delta`.
   - Run `scripts/run_retrospective_frontier_alignment_smoke.py` for the first
     deterministic TFR smoke, then run
     `scripts/run_retrospective_frontier_citation_probe.py` to replace manual
     future-frontier descriptors with citation-backed later-field evidence.
   - Run `scripts/run_review_frontier_signal_probe.py` to test whether the
     historical review snippets themselves carry future-frontier signals, and
     `scripts/run_semantic_frontier_judge_probe.py` when lexical overlap is too
     weak and a semantic judge over citation metadata is needed.
   - Treat delayed-value review signals as the high-value but hard case:
     review guidance may reduce short-term artifact quality while improving
     alignment with later mainstream or SOTA directions. If the probe finds no
     delayed-value cases, report that negative boundary directly.
   - Attach evidence, missing evidence, feasibility notes, and risks.
   - Ask the human scientist to select, merge, or rewrite directions using
     field taste, upside asymmetry, and failure value, not only early scores.
   - Use `docs/co_pilot_ai_scientist_v3/taste_insight_rubric.md` to record
     non-metric scientific taste without pretending it is a full reward model.
   - Trigger the first human gate: `scientific_taste_prior`.

3. **Stress-Test Evaluators**
   - Convert selected hypotheses into benchmarks, baselines, metrics, and
     runnable scripts.
   - Select benchmarks by claim type rather than defaulting to one suite. FML-
     bench is useful for AI Scientist-v2-style branch search, while
     MLAgentBench, ScienceAgentBench, MLE-bench, PaperBench, or custom
     machine-gradeable tasks may be better for other claims.
   - Maintain a benchmark-to-claim matrix that states what each benchmark can
     support and what it cannot prove yet. Use this matrix to choose the next
     run by the weakest unsupported claim.
   - Treat benchmark availability as evidence: if a benchmark's code is present
     but its private/verified data are absent, log that as a setup probe rather
     than reporting scores.
   - When official benchmark data are blocked, prefer a small controlled probe
     with explicit caveats over silently narrowing back to an easier benchmark.
   - For optimization tasks, add correctness gates before runtime or score
     optimization so fast invalid programs cannot win.
   - For fairness, safety, or robustness tasks, use multi-metric guardrails.
     Do not accept a branch on a single primary metric if a degenerate solution
     can game it; require a utility floor such as balanced accuracy or task
     success before continuation.
   - Trigger `evaluator_stress_test` before expensive runs.

4. **Steer The Frontier**
   - Use AI Scientist-v2-style tree search over experiment branches.
   - Log every branch, score, failure, and artifact path.
   - Trigger `frontier_steering` at fixed budget checkpoints.
   - Permit a human scientist to keep a branch that is not metric-best when it
     has stronger novelty, failure-analysis value, or high-tail upside.

5. **Run Verifiable Micro-Evolution**
   - When a subproblem is machine-gradeable, launch OpenEvolve as the
     open-source code-evolution layer used for verifiable micro-evolution.
   - State clearly that OpenEvolve is a substitute implementation because
     official AlphaEvolve is not open sourced.
   - Trigger `verifiable_micro_evolution` before escalating to expensive
     population search.

6. **Write and Calibrate Claims**
   - Generate the paper from actual logs, metrics, and citations.
   - Trigger `claim_calibration` to weaken, remove, or reframe unsupported
     claims before final polishing.
   - Produce bilingual usage notes when requested.

7. **Assemble Gate Trajectory**
   - Link scientific-taste, evaluator-stress, frontier-steering,
     micro-evolution, and claim-calibration gates into a trajectory artifact.
   - Mark whether the trajectory is a single online run or a retrospective
     chain assembled from separate probes.
   - Never use a retrospective gate chain as evidence of end-to-end
     performance superiority.
   - When archived experiment summaries already exist, run
     `scripts/run_full_gate_trajectory.py` to regenerate an executable
     artifact replay of the gate chain. Treat this as a reproducibility check,
     not as a substitute for a fresh online trajectory.
   - For a small fresh online smoke trajectory on the configured Ubuntu host,
     run `scripts/run_online_full_gate_smoke.py`, preferably with
     `--run-autonomous-baseline` and an explicit `--autonomous-steps` value.
     Treat a successful paired smoke run as orchestration evidence and a
     tiny-budget comparison, not as general superiority evidence.
   - After every online smoke or full trajectory, run or archive a matched
     autonomous baseline under the same task/model/step budget before making
     performance claims. Report negative comparisons directly.
   - When multiple FML matched comparisons are archived, run
     `scripts/summarize_fml_matched_comparisons.py` to report win counts, mean
     deltas, and the explicit statistical limitation before updating claims.
   - For any claim beyond pilot feasibility, assemble a prospective matched-
     budget package and run `scripts/audit_prospective_matched_budget_package.py`.
     If this audit fails, keep superiority, paper-quality, and attention-
     efficiency claims as hypotheses.
   - After the package audit passes, run
     `scripts/summarize_prospective_matched_packages.py` and report the metric
     direction, co-pilot score, autonomous score, winner, and claim implication.
     Do not treat a passed package audit as a positive performance result.
   - If the package contains a manuscript artifact, run
     `scripts/score_matched_manuscripts.py` to create a matched autonomous
     mini-manuscript and score anonymized A/B manuscript quality. Treat this as
     measurement-readiness unless full end-to-end manuscripts are scored.
   - For paired online full manuscripts, run
     `scripts/score_matched_manuscripts.py` with explicit
     `--co-pilot-manuscript`, `--autonomous-manuscript`, and `--output-dir`.
     Treat Monica-routed model reviews as audit evidence; do not call them
     independent human expert review.
   - After multiple same-run online paired smokes exist, run
     `scripts/summarize_online_paired_smokes.py --update-manifest`. Report
     co-pilot benchmark wins, autonomous wins, ties, mean metrics, and
     manuscript-review probes separately. Do not let positive manuscript-review
     probes override negative benchmark aggregates.
   - To check whether one archived matched package contains enough evidence for
     complete paper-shaped outputs, run
     `scripts/generate_full_manuscript_probe.py --update-manifest`. Treat this
     as archived-evidence manuscript generation, not as a fresh end-to-end
     research trajectory or independent paper-quality proof.
   - To generate a manuscript from a fresh online full-gate trajectory, run
     `scripts/generate_online_trajectory_manuscript.py` with `--trajectory-json`.
     When an autonomous summary is available, also pass
     `--autonomous-summary-json` to create a matched-budget autonomous
     manuscript comparator. Report this as a comparator artifact unless the
     autonomous manuscript comes from the same continuous online trajectory.
   - To turn real Codex project usage into a privacy-preserving process
     dataset, run `scripts/build_human_copilot_trace_dataset.py`. Treat the
     resulting `human_copilot_trace_dataset.md/json` as a single-author
     longitudinal trace corpus, not as population-level human-subject evidence.
   - Before releasing that derived trace dataset, run
     `scripts/audit_human_copilot_trace_dataset.py`. Report the audit status,
     required-field coverage, claim-boundary check, and secret/raw-log scan
     counts. A passing release audit reduces leakage risk; it does not replace
     human-subject review if the corpus expands beyond the author's own traces.
   - Do not use the author's single-user trace as the main population evidence
     for human-guided automated science. A true online co-pilot dataset would
     require a broadly deployed skill or assistant used by many researchers,
     consent and de-identification, and prospective logging of interventions,
     attention cost, artifacts, and downstream outcomes.
   - To check the package shape on a controlled remote computation, run
     `scripts/run_prospective_matched_budget_micro_pilot.py`; treat it only as
     evidence-shape validation, not as AI Scientist-v2 superiority evidence.
   - To create a small AI Scientist-v2-style prospective package, run
     `scripts/run_prospective_fml_matched_package.py` on the configured Ubuntu
     host, optionally passing `--task-config` and `--benchmark-slug` for the
     runnable FML workspace, then audit it. If no co-pilot branch produces a
     valid score, record `abort_no_valid_branch` and report the package as an
     invalid-continuation failure case rather than a performance win. Report
     negative matched results directly.

## Human Gate Schema

Each human intervention should be stored as structured data:

```json
{
  "gate_id": "frontier_gate_001",
  "gate_type": "frontier_steering",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "options": [],
  "human_decision": "",
  "rationale": "",
  "affected_artifacts": [],
  "downstream_budget": {},
  "attention_cost": {
    "active_review_minutes": null,
    "wall_clock_latency_minutes": null,
    "options_reviewed": null,
    "artifacts_reviewed_count": null,
    "decision_count": 1
  },
  "follow_up_checks": []
}
```

For prospective matched-budget runs, fill `attention_cost` at every human gate.
Do not estimate missing historical review time; run
`scripts/audit_human_gate_attention_cost.py` and report missing coverage as a
measurement gap.
Use `scripts/create_human_gate_log.py` during prospective runs to create a
schema-compatible gate log with active review minutes, wall-clock latency,
options reviewed, artifacts reviewed, decision count, and scientific
taste/insight fields. Use `--require-complete-attention` and
`--require-complete-taste` for matched-budget packages.

For gates where human scientific taste or insight changes the search frontier,
also fill `taste_insight` with the project rubric. Run
`scripts/audit_taste_insight_coverage.py` and report missing historical fields
as missing rather than reconstructing them after the fact.

## Model Routing

- Use lower-cost models such as DeepSeek for routine drafting, coding, and
  smoke tests.
- Use Monica-routed frontier GPT/Gemini/Anthropic models for high-leverage
  critique, hypothesis debate, claim audit, and final writing passes.
- Never print API keys in logs. Prefer environment variables already available
  in the global shell.

## OpenEvolve Integration

Use OpenEvolve for the programmatic-search module:

```bash
python3 -m pip install openevolve openai
python3 scripts/run_openevolve_program_search.py \
  --initial-program path/to/initial_program.py \
  --evaluator path/to/evaluator.py \
  --output-dir path/to/output/run \
  --iterations 5 \
  --provider deepseek \
  --model deepseek-chat
```

For Monica or other OpenAI-compatible providers, set the provider in the wrapper
arguments and expose the matching environment variables:

```bash
python3 scripts/run_openevolve_program_search.py \
  --initial-program path/to/initial_program.py \
  --evaluator path/to/evaluator.py \
  --output-dir path/to/output/run \
  --iterations 5 \
  --provider monica \
  --model gpt-4o-mini
```

Compare OpenEvolve against a direct LLM-edit baseline using the same evaluator,
iteration budget, and model routing before claiming the programmatic-search
module improves research quality. Current archived examples include function
minimization, knapsack, weighted Max-Cut, MLAgentBench vectorization, and
sklearn diabetes tabular regression.

If direct editing matches or beats OpenEvolve on a simple task, record that as
an escalation-boundary result. The program-search gate is meant to decide when
deeper search is worth the cost, not to force OpenEvolve onto every subproblem.

For runtime-optimization benchmarks, expose a single `combined_score` that
OpenEvolve should maximize, and keep raw metrics such as `runtime_seconds` for
reporting. Do not let "lower is better" fields get averaged into the search
objective.

## Templates

Reusable templates are stored next to this skill:

- `templates/task_spec_template.md`: task definition and gate plan.
- `templates/human_gate_log_template.json`: structured human gate log matching
  the project schema.
- `templates/claim_audit_template.md`: claim-by-claim paper audit.
- `docs/co_pilot_ai_scientist_v3/taste_insight_rubric.md`: project rubric for
  recording scientific taste, insight, and high-tail upside.

## Output Artifacts

- problem statement;
- candidate hypotheses and scores;
- literature and benchmark notes;
- benchmark-to-claim matrix;
- taste/insight rubric records;
- human gate logs;
- attention-cost logging smoke audit;
- attention+taste logging smoke audit;
- human attention-cost audit;
- taste/insight coverage audit;
- prospective matched-budget package audit;
- full-gate trajectory artifact;
- executable full-gate trace replay when archived summaries are available;
- online full-gate smoke trajectory logs when remote execution is available;
- online trajectory manuscript probes when an online full-gate trajectory needs
  to be rendered into a claim-audited manuscript artifact;
- repeated same-run online paired-smoke summaries when more than one
  same-continuous online trajectory is available;
- prospective matched-budget micro-pilot package when remote execution is
  available;
- matched mini- and full-manuscript generation probes when manuscript evidence
  is being audited. Use `--package-dir` to point the full-manuscript probe at
  the newest prospective package, and keep its limitation as archived-evidence
  manuscript generation unless the upstream run was genuinely fresh end-to-end;
- derived Human Co-Pilot Trace Dataset when human usage evidence is discussed;
- experiment logs and metrics;
- program-search traces;
- English and Chinese manuscript drafts;
- usage instructions;
- final reproducibility manifest.

## Quality Rules

- Do not invent results, citations, or benchmark numbers.
- Separate proposed architecture from verified experimental findings.
- Prefer narrow claims until logs prove broader claims.
- Reject metric-gaming results even when the primary metric improves.
- Distinguish retrospective gate-chain evidence from a true online end-to-end
  run with all gates active.
- Treat human decisions as high-variance search data, not informal chat context.
- Do not assume human participation always helps. Report negative results and
  distinguish mean benchmark performance from high-tail scientific upside.
- Keep the final paper aligned with actual experiment artifacts.
