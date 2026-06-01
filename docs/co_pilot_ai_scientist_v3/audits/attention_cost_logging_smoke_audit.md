# Human Gate Logging Smoke Audit

Audit date: 2026-06-01T18:04:30Z

This smoke test verifies that future human gates can be logged with
complete measurable attention-cost fields. The generated gate is synthetic
tooling evidence and is not counted as a real experiment-performance gate.

## Result

- Overall status: pass
- Generated gate log: `docs/co_pilot_ai_scientist_v3/audits/attention_cost_logging_smoke_gate.json`
- Complete attention-cost record: True
- Validation errors: 0

## Attention Cost

- `human_actor`: tooling_smoke
- `interaction_mode`: posthoc_replay
- `prompted_at_utc`: 2026-06-01T18:00:00Z
- `decision_at_utc`: 2026-06-01T18:04:30Z
- `active_review_minutes`: 3.5
- `wall_clock_latency_minutes`: 4.5
- `options_reviewed`: 2
- `artifacts_reviewed_count`: 1
- `decision_count`: 1
- `notes`: Synthetic gate used to validate prospective attention-cost logging tooling; not a real experiment-performance gate.

## Interpretation

The current archived human-gate logs still lack measured attention cost,
but the package now includes a runnable path for prospective gates to
record active review minutes, wall-clock latency, options reviewed,
artifacts reviewed, and decision count.
