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

For a Monica-routed paper-quality review, source the global environment and run:

```bash
source ~/.codex/env
python3 scripts/run_paper_quality_review.py \
  --models gpt-4o-mini claude-3-7-sonnet-latest \
  --max-tokens 4096
```

Treat the output as review evidence, not as proof of acceptance.

## Human Gate Types

- `idea_selection`: choose or rewrite the research hypothesis.
- `evaluator_approval`: approve metrics, baselines, and failure conditions.
- `branch_selection`: choose which experiment branches receive more budget.
- `program_search_escalation`: decide whether a subproblem deserves deeper
  code evolution.
- `claim_audit`: remove or weaken unsupported paper claims.

## Environment

Use API keys from global environment variables. Suggested routing:

- DeepSeek for low-cost coding and smoke runs.
- Monica-routed GPT/Gemini/Anthropic models for hypothesis debate, high-stakes
  review, and final writing.
- Ubuntu SSH host for heavier benchmark execution.

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
