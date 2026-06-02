# External Clean Skill Reuse Task

## Run ID

`external_clean_skill_reuse_smoke_20260603`

## External Workspace

`/private/tmp/copilot_v3_external_skill_reuse_smoke/workspace`

## Fresh Topic

Design a co-pilot workflow for a small scientific-visualization replication
study. The task is intentionally outside the paper's FML, OpenReview replay,
and toy tabular-evaluator narratives. The goal is to check whether the release
skill can be reused in a clean external workspace on a new research style.

## AI Scientist-v2 Base Loop

1. Frame a reproducible visualization-replication question.
2. Generate candidate tasks: chart reproduction, data-cleaning audit, and
   figure-claim consistency.
3. Select a benchmark or fixed rubric.
4. Run small executable checks when data are available.
5. Draft a report only from logged evidence.
6. Calibrate claims before any paper-quality statement.

## IGRE Six-Gate Overlay

- `scientific_taste_prior`: prioritize figure-claim consistency because it
  exposes a high-value failure mode in automated science.
- `evaluator_stress_test`: require the rubric to distinguish visual similarity
  from scientific claim correctness.
- `frontier_steering`: allocate effort to the branch with the strongest
  diagnostic failure value, not merely the easiest chart.
- `verifiable_micro_evolution`: trigger only for machine-gradeable parsing or
  plotting subroutines.
- `structured_feedback`: route reviewer comments into figure, data, and claim
  fixes separately.
- `claim_calibration`: report this smoke as external clean-environment reuse,
  not as a benchmark or human-review result.

## Failure Criteria

- The skill cannot be read from the external temporary Codex skills directory.
- The generated plan omits the AI Scientist-v2 base loop or any IGRE gate.
- The claim audit presents engineering reuse as scientific superiority.
