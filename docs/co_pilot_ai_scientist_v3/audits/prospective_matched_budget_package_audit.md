# Prospective Matched-Budget Package Audit

This audit checks whether the repository contains a prospective matched-budget
run that can support stronger Co-Pilot AI Scientist v3 claims. It is stricter
than the artifact manifest: synthetic smoke logs and retrospective replays do
not count as qualifying performance evidence.

## Summary

- Overall status: `pass`
- Manifest files checked: 2
- Passing packages: 2
- Failing packages: 0

## `prospective_matched_fml_causality_20260602_000001`

- Status: `pass`
- Gate records checked: 1
- Complete attention-cost gates: 1
- Complete taste/insight gates: 1
- Errors: 0


## `prospective_matched_micro_pilot_20260602_000001`

- Status: `pass`
- Gate records checked: 1
- Complete attention-cost gates: 1
- Complete taste/insight gates: 1
- Errors: 0


## Interpretation

At least one non-synthetic package now satisfies the minimum
prospective matched-budget evidence shape. This permits the paper to
state that the evaluation package can be produced and audited, but it
does not by itself prove top-conference-level performance. Strong
claims about paper quality, human-attention efficiency, or superiority
over autonomous AI Scientist-v2 still require larger tasks, more seeds,
and independent paper-quality evaluation.
