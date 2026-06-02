# Co-Pilot AI Scientist v3 Task Spec

## Research Task ID

`global_skill_reuse_smoke_20260603`

## Topic

Design a small, automatically auditable study of whether review-derived
evaluator-stress gates can prevent metric gaming in a toy tabular ML task. The
task is intentionally outside the existing paper's main replay cases so that it
tests global skill reuse rather than reusing the original package narrative.

## Success Criteria

- Primary benchmark metric: valid-run rate under a guarded evaluator.
- Minimum acceptable improvement: at least one degenerate primary-metric winner
  must be rejected by the evaluator-stress gate in a future executable run.
- Paper-quality target: produce a claim-calibrated mini-report from logs only.
- Reproducibility target: every gate must have a JSON log and every claim must
  cite an artifact path.
- Taste/insight target:
  - The non-metric factor is whether a metric captures the intended scientific
    target rather than merely rewarding a shortcut.
  - A high-tail outcome would be identifying an evaluator flaw before spending
    budget on a misleading branch.

## Failure Criteria

- The evaluator cannot distinguish degenerate shortcuts from valid models.
- The gate changes no control decision and only acts as extra prose.
- No autonomous baseline is available for comparison.

## Human Gates

- `scientific_taste_prior`: keep the task because evaluator reliability is a
  core risk in automated science.
- `long_horizon_taste_gate`: no delayed-value claim in this smoke.
- `evaluator_stress_test`: inspect whether the primary metric can be gamed.
- `frontier_steering`: allocate budget only after the evaluator-stress gate.
- `verifiable_micro_evolution`: trigger only if the evaluator is
  machine-gradeable and has a correctness guardrail.
- `claim_calibration`: report this as global skill reuse evidence only.

## Baselines

- Autonomous AI Scientist-v2 style run: primary metric only.
- Direct LLM rewrite or sampling baseline: not run in this engineering smoke.
- Existing method or benchmark baseline: guarded-evaluator toy baseline.

## Machine-Gradeable Subproblems

- Subproblem: metric-gaming detection for a toy tabular evaluator.
- Evaluator path: to be implemented in a future executable run.
- Initial program path: not applicable for this template smoke.
- OpenEvolve budget: none in this engineering smoke.

## Expected Artifacts

- Human gate logs: `human_gate_log.json`.
- Experiment logs: none; this is a global installed-skill reuse smoke.
- Program-search traces: none.
- Paper draft: none.
- Reproducibility manifest update: `repro_manifest.json`.
