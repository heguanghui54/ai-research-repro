# Benchmark Coverage Audit

- Audit date: `2026-06-02T19:00:16Z`
- Status: `pass`
- FML entries: `2`
- Non-FML entries: `11`

## Positive Scored Evidence

- MLAgentBench vectorization: `8/8` correct best programs; median runtime `0.024580717086791992` seconds versus starter `3.261186361312866` seconds; direct rewrite correctness `False`.
- Program search subproblems: knapsack OpenEvolve `0.9994394752555711` versus direct `0.9952700988954383`; Max-Cut OpenEvolve-minus-direct `0.0085959186678094`.
- Open-data evaluator-stress pilot: `5` sklearn tasks, `5` split seeds, `25` paired selections, `8` candidates each, co-pilot mean balanced accuracy `0.9264256134480804` versus autonomous `0.9248566268790939`, delta `0.00156898656898655`; selection changed in `4` paired selections.
- Evaluator-stress trigger policy: best policy `class_imbalance_trigger_0_94` with delta `0.003076923076923066` versus always-on delta `0.00156898656898655`.
- Held-out trigger-policy validation: best policy `class_imbalance_trigger_0_94` with delta `0.003639444256184343` versus held-out always-on delta `0.0025821297988698876`.
- Frozen trigger-policy transfer: discovery selected `class_imbalance_trigger_0_94`; held-out frozen delta `0.003639444256184343` versus held-out always-on delta `0.0025821297988698876`, with held-out losses `0` versus always-on losses `2`.

## Boundary And Blocked Evidence

- sklearn diabetes boundary: direct rewrite RMSE `55.89546025654621` matches or beats OpenEvolve median `55.89546025654621`, so program search should be gated rather than automatic.
- `mlagentbench_cifar10`: `setup_blocked_by_slow_dataset_download`; no official score reported.
- `mlagentbench_cifar10_refresh`: `blocked_slow_data_download`; no official score reported.
- `mlagentbench_imdb`: `setup_blocked_by_huggingface_network`; no official score reported.
- `mlagentbench_clrs`: `blocked_cpu_timeout_no_checkpoint`; no official score reported.
- `mlagentbench_clrs_reduced`: `blocked_reduced_cpu_timeout_no_checkpoint`; no official score reported.
- `mlagentbench_house_price`: `setup_blocked_by_missing_kaggle_cli_and_competition_consent`; no official score reported.
- `scienceagentbench`: `metadata_and_verified_artifacts_not_yet_accessible`; no official score reported.

## Checks

- `benchmark_claim_matrix_has_entries`: `pass`
- `fml_evidence_represented`: `pass`
- `non_fml_evidence_represented`: `pass`
- `matrix_records_boundaries`: `pass`
- `selection_mentions_beyond_fml`: `pass`
- `mlagentbench_vectorization_scored_multiseed`: `pass`
- `mlagentbench_vectorization_all_correct`: `pass`
- `mlagentbench_vectorization_all_faster_than_starter`: `pass`
- `mlagentbench_direct_rewrite_failed_correctness`: `pass`
- `mlagentbench_median_runtime_beats_starter`: `pass`
- `knapsack_openevolve_beats_direct`: `pass`
- `maxcut_openevolve_beats_direct`: `pass`
- `sklearn_boundary_direct_matches_or_beats_openevolve`: `pass`
- `open_data_multitask_evaluator_stress_scored`: `pass`
- `evaluator_stress_trigger_policy_scored`: `pass`
- `evaluator_stress_trigger_policy_heldout_scored`: `pass`
- `evaluator_stress_trigger_policy_transfer_validated`: `pass`
- `blocked_official_tasks_logged`: `pass`
- `blocked_tasks_do_not_report_scores`: `pass`
- `mlagentbench_clrs_dependency_repaired_but_unscored`: `pass`
- `mlagentbench_clrs_reduced_kept_non_official_and_unscored`: `pass`
- `mlagentbench_house_price_credential_blocker_logged`: `pass`
- `stretch_targets_kept_future`: `pass`

## Errors

- None

## Warnings

- MLAgentBench vectorization speedups are positive but seed-sensitive.
- Max-Cut OpenEvolve advantage is small and single-seed.

## Claim Boundary

Benchmark coverage now includes FML feasibility evidence, non-FML scored program-search probes, an open-data multi-task evaluator-stress pilot, a direct-editing boundary condition, and logged official benchmark blockers. This supports selective workflow design, not whole-paper superiority over autonomous AI Scientist-v2.
