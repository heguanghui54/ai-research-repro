# Co-Pilot AI Scientist v3 Task Spec

## Research Task ID

`skill_reuse_smoke_001`

## Topic

Validate that the Co-Pilot AI Scientist v3 Codex skill can be reused on a new
research task without relying on the original chat context.

## Success Criteria

- Primary benchmark metric: all required skill artifacts validate locally.
- Minimum acceptable improvement: generated gate log conforms to schema.
- Paper-quality target: claims stay grounded in audit outputs.
- Reproducibility target: clean clone can rerun the validation script.
- Taste/insight target:
  - Which non-metric scientific factor matters most? Benchmark-to-claim fit.
  - What high-tail outcome would justify preserving a risky branch? A branch
    that exposes an evaluator flaw or stronger research question.

## Failure Criteria

- Missing skill instructions, templates, or schema.
- Generated human gate cannot be validated.
- The skill encourages unsupported performance claims.

## Human Gates

- `scientific_taste_prior`: choose claim-matched benchmarks over convenient benchmarks.
- `evaluator_stress_test`: reject metric-gaming or invalid evaluators.
- `frontier_steering`: preserve high-upside branches at budget checkpoints.
- `verifiable_micro_evolution`: escalate machine-gradeable subproblems only when warranted.
- `claim_calibration`: weaken unsupported paper claims before PDF build.

## Baselines

- Autonomous AI Scientist-v2 style run: required for future matched experiments.
- Direct LLM rewrite or sampling baseline: required for program-search comparisons.
- Existing method or benchmark baseline: selected by claim type.

## Machine-Gradeable Subproblems

- Subproblem: skill-template validation.
- Evaluator path: `scripts/validate_copilot_skill.py`.
- Initial program path: not applicable.
- OpenEvolve budget: not launched for this smoke test.

## Expected Artifacts

- Human gate logs: `skill_reuse_smoke_human_gate_log.json`.
- Experiment logs: `skill_reuse_smoke_audit.json`.
- Program-search traces: not applicable for this smoke test.
- Paper draft: not generated in this smoke test.
- Reproducibility manifest update: required after audit.
