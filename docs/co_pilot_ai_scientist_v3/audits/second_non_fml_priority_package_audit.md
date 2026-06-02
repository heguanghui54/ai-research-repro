# Second Non-FML Priority Package Audit

- Audit date: `2026-06-02T21:35:28Z`
- Status: `pass`
- Evidence class: `scored_official_mlagentbench_non_fml_plus_official_like_package`
- Priority queue item: `Second scored non-FML benchmark package`
- Official MLAgentBench CIFAR10 baseline score: `0.5103`
- Official MLAgentBench CIFAR10 co-pilot selected score: `0.7782`
- Official MLAgentBench CIFAR10 delta: `0.2679`
- Official MLAgentBench CIFAR10 multi-seed mean score: `0.7743`
- Official MLAgentBench CIFAR10 multi-seed min score: `0.7709`
- Official MLAgentBench CIFAR10 multi-seed sample std: `0.003675595189897806`
- Train package: `prospective_matched_open_data_multitask_20260603`
- Held-out package: `prospective_matched_open_data_multitask_holdout_20260603`
- Selected trigger policy: `class_imbalance_trigger_0_94`

## Train Summary

- Mean delta: `0.00156898656898655`
- Wins/losses/ties: `2` / `2` / `21`
- Selection changes: `4`

## Held-Out Frozen Policy

- Frozen-policy delta: `0.003639444256184343`
- Wins/losses/ties: `2` / `0` / `23`

## Official Benchmark Boundary

- `mlagentbench_cifar10_refresh`: status `blocked_slow_data_download`, score reported `False`
- `mlagentbench_imdb`: status `setup_blocked_by_huggingface_network`, score reported `False`
- `mlagentbench_clrs`: status `blocked_cpu_timeout_no_checkpoint`, score reported `False`
- `mlagentbench_clrs_reduced`: status `blocked_reduced_cpu_timeout_no_checkpoint`, score reported `False`
- `mlagentbench_house_price`: status `setup_blocked_by_missing_kaggle_cli_and_competition_consent`, score reported `False`
- `scienceagentbench`: status `metadata_and_verified_artifacts_not_yet_accessible`, score reported `False`

## Errors

- None

## Claim Boundary

This closes a low-cost official-like non-FML matched-package gap: the package is scored, open-data, matched, held-out, and auditable; it also adds a three-seed scored official MLAgentBench CIFAR10/debug result. The evidence is still one official task plus one official-like package, not broad AI Scientist-v2 paper-quality superiority.
