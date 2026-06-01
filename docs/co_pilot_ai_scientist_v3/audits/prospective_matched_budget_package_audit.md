# Prospective Matched-Budget Package Audit

This audit checks whether the repository contains a prospective matched-budget
run that can support stronger Co-Pilot AI Scientist v3 claims. It is stricter
than the artifact manifest: synthetic smoke logs and retrospective replays do
not count as qualifying performance evidence.

## Summary

- Overall status: `fail_no_passing_prospective_package`
- Manifest files checked: 0
- Passing packages: 0
- Failing packages: 0

No prospective matched-budget package manifests were found.

A qualifying package must provide:

1. A co-pilot trajectory generated prospectively.
2. A matched autonomous baseline on the same task/model/tool budget.
3. Complete `attention_cost` records for every human gate.
4. Complete `taste_insight` records for every human gate.
5. A final claim audit and manuscript generated from the same run.

## Interpretation

Until this audit passes on at least one non-synthetic package, the paper
should not claim that IGRE improves paper quality, human-attention
efficiency, or autonomous AI Scientist-v2 performance. Passing this audit
would not by itself prove top-conference-level results, but it is the
minimum evidence shape needed before those claims can be evaluated.
