# MLAgentBench OGBN-arxiv Multi-Seed Audit

- Audit date: `2026-06-02T22:24:10Z`
- Status: `pass`
- Evidence class: `three_seed_scored_official_mlagentbench_ogbn_arxiv_compatibility_path`
- Task: `ogbn-arxiv`
- Metric: `OGBN-arxiv test accuracy from official MLAgentBench eval.py; higher is better`
- Compatibility baseline score: `0.02744686541983005`
- Seed scores: `[0.5399872435857869, 0.5408925374976853, 0.5436289940950148]`
- Mean score: `0.5415029250594956`
- Min score: `0.5399872435857869`
- Sample std: `0.0018960528538453166`
- Mean delta vs baseline: `0.5140560596396655`

## Per-Seed Checks

- Seed `20260603`: train completed `pass`, eval log match `pass`, beats baseline `pass`
- Seed `20260604`: train completed `pass`, eval log match `pass`, beats baseline `pass`
- Seed `20260605`: train completed `pass`, eval log match `pass`, beats baseline `pass`

## Checks

- `all_required_files_present`: `pass`
- `seed_count_at_least_three`: `pass`
- `all_train_logs_completed`: `pass`
- `all_eval_logs_match_summary`: `pass`
- `all_seeds_beat_baseline`: `pass`
- `mean_score_matches_summary`: `pass`
- `min_score_matches_summary`: `pass`
- `sample_std_matches_summary`: `pass`
- `compatibility_boundary_recorded`: `pass`

## Errors

- None

## Claim Boundary

Three co-pilot-selected seeds under the official OGBN-arxiv evaluator support robustness of the compatibility path. The baseline remains a compatibility translation rather than the unmodified NeighborLoader starter, so this is not broad MLAgentBench superiority evidence.
