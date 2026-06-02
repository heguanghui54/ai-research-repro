# Co-Pilot AI Scientist v3 Task Spec

## Research Task ID

`task_id_here`

## Topic

One paragraph describing the research problem.

## Success Criteria

- Primary benchmark metric:
- Minimum acceptable improvement:
- Paper-quality target:
- Reproducibility target:
- Taste/insight target:
  - Which non-metric scientific factor matters most?
  - What high-tail outcome would justify preserving a risky branch?

## Failure Criteria

- What result would make the hypothesis unsupported?
- What evaluator flaw would invalidate the run?
- What budget limit stops the branch?

## Human Gates

- `scientific_taste_prior`:
- `long_horizon_taste_gate`:
  - Is there any human review or expert comment that may reduce short-term
    artifact quality but point toward later field trajectories?
  - What historical paper, review text, later-field evidence, paper-only
    control, and shuffled-review control would make this testable?
- `evaluator_stress_test`:
- `frontier_steering`:
- `verifiable_micro_evolution`:
- `claim_calibration`:

## Prospective Gate Instrumentation

For any matched-budget or paper-quality claim, every human gate must be created
with `scripts/create_human_gate_log.py` using both:

```bash
--require-complete-attention --require-complete-taste
```

Required `attention_cost` fields:

- `active_review_minutes`
- `wall_clock_latency_minutes`
- `options_reviewed`
- `artifacts_reviewed_count`
- `decision_count`

Required `taste_insight` fields:

- `rubric_version`
- all rubric `scores`
- `taste_insight_score`
- `qualitative_rationale`
- `non_metric_factors`

If any prospective gate is missing these fields, the run may still be archived
as a smoke or engineering artifact, but it cannot support attention-efficiency,
human-taste, or top-conference superiority claims.

## Taste/Insight Rubric

- Use `docs/co_pilot_ai_scientist_v3/taste_insight_rubric.md`.
- Record `taste_insight` in every prospective gate where qualitative scientific
  judgment changes the search frontier.
- If the decision is a long-horizon override, record whether it is a candidate
  Delayed-Value Review Signal (DVRS), the expected short-term cost, and the
  later-frontier evidence needed for validation.
- Do not optimize the agent directly against this score; use it as an auditable
  search prior and compare downstream outcomes against autonomous baselines.

## Baselines

- Autonomous AI Scientist-v2 style run:
- Direct LLM rewrite or sampling baseline:
- Existing method or benchmark baseline:
- For TFR/LHTG tests, paper-only replay:
- For TFR/LHTG tests, shuffled-review-control replay:

## Machine-Gradeable Subproblems

- Subproblem:
- Evaluator path:
- Initial program path:
- OpenEvolve budget:

## Expected Artifacts

- Human gate logs:
- Experiment logs:
- Program-search traces:
- Delayed-value candidate queue or TFR replay artifacts:
- Paper draft:
- Reproducibility manifest update:
