---
name: co-pilot-ai-scientist-v3
description: Human-in-the-loop automated research workflow that combines AI Co-Scientist-style hypothesis generation, AI Scientist-v2-style experiment and paper automation, and AlphaEvolve/OpenEvolve-style programmatic search.
---

# Co-Pilot AI Scientist v3

## Purpose

Run collaborative automated research where human scientists intervene at
high-leverage creative, evaluation, search, and claim-audit nodes.

## Use This Skill When

- A user wants to turn a broad research idea into a paper with human guidance.
- A project should combine hypothesis generation, benchmark execution, paper
  writing, and code-evolution subproblem search.
- The user wants a co-pilot workflow rather than a fully autonomous pipeline.
- Human feedback must be logged as part of the reproducibility record.

## Core Workflow

1. **Frame**
   - Convert the topic into a testable research question.
   - Define success metrics, failure conditions, and target venue level.

2. **Generate Hypotheses**
   - Use multiple agents or model passes to generate, critique, and refine
     hypotheses.
   - Attach evidence, missing evidence, feasibility notes, and risks.
   - Trigger the first human gate: `idea_gate`.

3. **Design Evaluators**
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
   - Trigger `evaluator_gate` before expensive runs.

4. **Run Agentic Search**
   - Use AI Scientist-v2-style tree search over experiment branches.
   - Log every branch, score, failure, and artifact path.
   - Trigger `branch_gate` at fixed budget checkpoints.

5. **Optimize Subproblems**
   - When a subproblem is machine-gradeable, launch OpenEvolve as the
     open-source AlphaEvolve-style code evolution layer.
   - State clearly that OpenEvolve is a substitute implementation because
     official AlphaEvolve is not open sourced.
   - Trigger `program_search_gate` before escalating to expensive evaluation.

6. **Write and Audit**
   - Generate the paper from actual logs, metrics, and citations.
   - Trigger `claim_gate` to audit unsupported claims before final polishing.
   - Produce bilingual usage notes when requested.

7. **Assemble Gate Trajectory**
   - Link idea, evaluator, branch, program-search, and claim gates into a
     trajectory artifact.
   - Mark whether the trajectory is a single online run or a retrospective
     chain assembled from separate probes.
   - Never use a retrospective gate chain as evidence of end-to-end
     performance superiority.
   - When archived experiment summaries already exist, run
     `scripts/run_full_gate_trajectory.py` to regenerate an executable
     artifact replay of the gate chain. Treat this as a reproducibility check,
     not as a substitute for a fresh online trajectory.

## Human Gate Schema

Each human intervention should be stored as structured data:

```json
{
  "gate_id": "branch_gate_001",
  "gate_type": "branch_selection",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "options": [],
  "human_decision": "",
  "rationale": "",
  "affected_artifacts": [],
  "downstream_budget": {},
  "follow_up_checks": []
}
```

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
module improves research quality.

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

## Output Artifacts

- problem statement;
- candidate hypotheses and scores;
- literature and benchmark notes;
- benchmark-to-claim matrix;
- human gate logs;
- full-gate trajectory artifact;
- executable full-gate trace replay when archived summaries are available;
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
- Treat human decisions as data, not informal chat context.
- Keep the final paper aligned with actual experiment artifacts.
