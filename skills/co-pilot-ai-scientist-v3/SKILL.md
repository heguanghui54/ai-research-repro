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

## Use This Skill When

- A user wants to turn a broad research idea into a paper with human guidance.
- A project needs hypothesis generation, benchmark execution, paper writing,
  and code-evolution subproblem search organized as one co-pilot method rather
  than a loose combination of prior systems.
- The user wants a co-pilot workflow rather than a fully autonomous pipeline.
- Human feedback must be logged as part of the reproducibility record.
- The evaluation should consider both mean benchmark performance and the chance
  of rare high-novelty, high-impact research outcomes.

## Core Workflow

1. **Frame**
   - Convert the topic into a testable research question.
   - Define success metrics, failure conditions, and target venue level.

2. **Set Scientific Taste Prior**
   - Use multiple agents or model passes to generate, critique, and refine
     hypotheses.
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
     run `scripts/run_online_full_gate_smoke.py`. Treat a successful smoke run
     as orchestration evidence only until a matched autonomous baseline exists.
   - After every online smoke or full trajectory, run or archive a matched
     autonomous baseline under the same task/model/step budget before making
     performance claims. Report negative comparisons directly.
   - For any claim beyond pilot feasibility, assemble a prospective matched-
     budget package and run `scripts/audit_prospective_matched_budget_package.py`.
     If this audit fails, keep superiority, paper-quality, and attention-
     efficiency claims as hypotheses.
   - To check the package shape on a controlled remote computation, run
     `scripts/run_prospective_matched_budget_micro_pilot.py`; treat it only as
     evidence-shape validation, not as AI Scientist-v2 superiority evidence.

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
- prospective matched-budget micro-pilot package when remote execution is
  available;
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
