# Global Skill Engineering Chain Audit

- Audit date: `2026-06-02T18:09:05Z`
- Status: `pass`
- Steps passed: `6/6`

## Steps

- `standalone_release_scaffold`: `pass`
- `isolated_install_smoke`: `pass`
- `global_install_audit`: `pass`
- `global_reuse_smoke`: `pass`
- `external_clean_reuse_smoke`: `pass`
- `toy_evaluator_stress_link`: `pass`

## Toy Evaluator Link

- Primary-only winner: `metric_gaming_all_negative`
- Evaluator-stress winner: `guardrailed_utility_model`
- Metric-gaming incidents reduced: `1`

## External Clean Reuse

- External root: `/private/tmp/copilot_v3_external_skill_reuse_smoke`
- Fresh topic: `scientific_visualization_replication`
- Six gates present: `True`

## Source Artifacts

- `release_manifest`: `release/co-pilot-ai-scientist-v3-skill/MANIFEST.json`
- `release_audit`: `docs/co_pilot_ai_scientist_v3/audits/igre_skill_release_package_audit.json`
- `isolated_install_smoke`: `docs/co_pilot_ai_scientist_v3/experiments/igre_skill_install_smoke_20260603/summary.json`
- `global_install_audit`: `docs/co_pilot_ai_scientist_v3/audits/global_copilot_skill_install_audit.json`
- `global_reuse_smoke`: `docs/co_pilot_ai_scientist_v3/experiments/global_skill_reuse_smoke_20260603/summary.json`
- `external_clean_reuse_smoke`: `docs/co_pilot_ai_scientist_v3/experiments/external_clean_skill_reuse_smoke_20260603/summary.json`
- `toy_evaluator_stress`: `docs/co_pilot_ai_scientist_v3/experiments/global_skill_metric_gaming_evaluator_20260603/summary.json`

## Errors

- None

## Warnings

- None

## Claim Boundary

This audit verifies the engineering chain from standalone release scaffold through isolated install, global install, fresh global-skill reuse, clean external temporary reuse, and one toy evaluator-stress smoke. It is usability and reproducibility evidence, not independent human evidence, not an official benchmark result, and not proof that Co-Pilot AI Scientist v3 outperforms autonomous AI Scientist-v2.
