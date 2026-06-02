# MLAgentBench CIFAR10 Multi-Seed Audit

- Audit date: `2026-06-02T21:35:28Z`
- Status: `pass`
- Evidence class: `scored_official_mlagentbench_non_fml_multiseed_task`
- Task: `MLAgentBench debug / cifar10`
- Metric: `CIFAR10 test accuracy; higher is better`
- Baseline score: `0.5103`
- Seed count: `3`
- Mean co-pilot-selected score: `0.7743`
- Min co-pilot-selected score: `0.7709`
- Max co-pilot-selected score: `0.7782`
- Sample std: `0.003676`
- Mean delta vs baseline: `0.2640`
- Min delta vs baseline: `0.2606`
- All seeds beat baseline: `True`

## Seed Results

| Seed | Official score | Delta vs baseline | Completed |
| --- | ---: | ---: | --- |
| `20260603` | `0.7782` | `0.2679` | `True` |
| `20260604` | `0.7709` | `0.2606` | `True` |
| `20260605` | `0.7738` | `0.2635` | `True` |

## Errors

- None

## Claim Boundary

This is a three-seed robustness check for one official MLAgentBench CIFAR10/debug task. It strengthens the non-FML evidence slice but remains one task and does not prove broad co-pilot superiority, paper-quality improvement, or independent human benefit.
