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
  --program-iterations 1
```

This runs FML-bench and OpenEvolve remotely. It is intended to prove
orchestration feasibility; it still needs a matched autonomous baseline before
any performance claim.

The archived smoke has a matched autonomous comparison in
`experiments/online_smoke_matched_autonomous_comparison.md`. The autonomous
baseline wins on held-out test MAE, so use it as a negative-result template.

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

The current archive has 1 complete taste/insight record, from the author's
benchmark-portfolio and high-tail framing decision, and 17 older records without
the field. Treat this as initial logging coverage, not as a performance result
about human scientific taste.

To check whether the repository contains a qualifying prospective matched-budget
package, run:

```bash
python3 scripts/audit_prospective_matched_budget_package.py
```

This audit is the hard gate before stronger claims. It passes only when a
non-synthetic package contains a prospective co-pilot trajectory, a matched
autonomous baseline, complete `attention_cost` and `taste_insight` records for
all human gates, a claim audit, and a manuscript from the same run.

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
  --max-steps 2
python3 scripts/audit_prospective_matched_budget_package.py
```

The archived FML package is a negative result for co-pilot performance at this
budget, so treat it as pilot evidence and a template for larger runs.

## Human Gate Types

- `scientific_taste_prior`: choose or rewrite the research hypothesis using
  scientific taste and upside, not only current scores.
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
