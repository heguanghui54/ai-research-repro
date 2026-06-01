# Prospective Matched-Budget Protocol

This protocol defines the minimum evidence shape required before Co-Pilot AI
Scientist v3 can make strong claims about human-gated research quality,
attention efficiency, or superiority over autonomous AI Scientist-v2.

The protocol is intentionally stricter than the current pilot package. Archived
smoke tests, retrospective gate chains, and synthetic logging checks are useful
engineering artifacts, but they do not count as qualifying performance evidence.

## Required Package Shape

A qualifying run should create a directory like:

```text
docs/co_pilot_ai_scientist_v3/experiments/prospective_matched_<run_id>/
  prospective_manifest.json
  co_pilot_trajectory.json
  autonomous_baseline_summary.json
  human_gate_logs/
  claim_audit.md
  manuscript.md
```

The `prospective_manifest.json` file must include:

- `package_id`
- `status`
- `co_pilot_trajectory`
- `autonomous_baseline`
- `human_gate_logs`
- `claim_audit`
- `manuscript`
- `matched_budget`

The `matched_budget` block must explicitly mark these as true:

- `same_task`
- `same_model_family`
- `same_step_budget`
- `same_tool_access`

## Required Human Gate Fields

Every human gate in the package must have complete `attention_cost` fields:

- `active_review_minutes`
- `wall_clock_latency_minutes`
- `options_reviewed`
- `artifacts_reviewed_count`
- `decision_count`

Every human gate must also have complete `taste_insight` fields:

- `rubric_version`
- `scores`
- `taste_insight_score`
- `qualitative_rationale`
- `non_metric_factors`

The point is not to prove that human input is always helpful. The point is to
make it possible to test whether human scientific taste changes the search
distribution, especially the high-tail outcomes that average task scores may
miss.

## Audit Command

Run:

```bash
python3 scripts/audit_prospective_matched_budget_package.py
```

The audit passes only if at least one non-synthetic prospective matched-budget
package satisfies the required artifact, attention-cost, taste/insight, and
budget-matching checks.

Current status: no qualifying prospective package exists yet. This is a real
top-conference evidence gap, not a formatting issue.
