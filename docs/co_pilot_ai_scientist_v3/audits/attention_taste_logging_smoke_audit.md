# Human Gate Logging Smoke Audit

Audit date: 2026-06-02T02:06:00Z

This smoke test verifies that future human gates can be logged with
complete measurable attention-cost fields. The generated gate is synthetic
tooling evidence and is not counted as a real experiment-performance gate.

## Result

- Overall status: pass
- Generated gate log: `docs/co_pilot_ai_scientist_v3/audits/attention_taste_logging_smoke_gate.json`
- Complete attention-cost record: True
- Complete taste/insight record: True
- Validation errors: 0

## Attention Cost

- `human_actor`: tooling_smoke
- `interaction_mode`: posthoc_replay
- `prompted_at_utc`: 2026-06-02T02:00:00Z
- `decision_at_utc`: 2026-06-02T02:06:00Z
- `active_review_minutes`: 4.25
- `wall_clock_latency_minutes`: 6.0
- `options_reviewed`: 2
- `artifacts_reviewed_count`: 2
- `decision_count`: 1
- `notes`: Synthetic gate used to validate prospective attention-cost plus taste/insight logging; not a real experiment-performance gate.

## Taste/Insight

- `rubric_version`: 2026-06-02
- `scores`: {'problem_depth': 5.0, 'novelty_potential': 4.0, 'mechanistic_value': 4.0, 'failure_informativeness': 5.0, 'benchmark_taste': 5.0, 'claim_significance': 4.0, 'risk_asymmetry': 4.0}
- `taste_insight_score`: 4.43
- `qualitative_rationale`: Claim-matched benchmark choice is a scientific-taste prior because it changes what the system searches for before metric outcomes are known.
- `non_metric_factors`: ['benchmark-choice-as-scientific-taste', 'high-tail-research-upside']

## Interpretation

The current archived human-gate logs still lack measured attention cost,
but the package now includes a runnable path for prospective gates to
record active review minutes, wall-clock latency, options reviewed,
artifacts reviewed, decision count, and optional scientific
taste/insight fields required by prospective matched-budget runs.
