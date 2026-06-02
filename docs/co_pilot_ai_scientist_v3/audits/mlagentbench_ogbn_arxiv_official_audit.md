# MLAgentBench OGBN-arxiv Official-Evaluator Audit

- Audit date: `2026-06-02T22:24:10Z`
- Status: `pass`
- Evidence class: `scored_official_mlagentbench_non_fml_task_with_compatibility_baseline`
- Task: `ogbn-arxiv`
- Metric: `OGBN-arxiv test accuracy from official MLAgentBench eval.py; higher is better`
- Baseline: `full_batch_compatibility_starter_translation` score `0.02744686541983005`
- Co-pilot selected: `full_batch_normalized_adamw_mlp` score `0.5399872435857869`
- Delta: `0.5125403781659569`

## Checks

- `all_required_files_present`: `pass`
- `official_prepared_data`: `pass`
- `official_eval_script`: `pass`
- `baseline_train_completed`: `pass`
- `baseline_eval_completed`: `pass`
- `candidate_train_completed`: `pass`
- `candidate_eval_completed`: `pass`
- `candidate_beats_baseline`: `pass`
- `compatibility_boundary_recorded`: `pass`
- `no_broad_superiority_claim`: `pass`

## Errors

- None

## Claim Boundary

This scored official-evaluator OGBN-arxiv run supports non-FML benchmark expansion and dependency-aware official task repair. Because the starter baseline is a compatibility translation rather than the unmodified NeighborLoader starter, it should not be used as broad MLAgentBench superiority evidence.
