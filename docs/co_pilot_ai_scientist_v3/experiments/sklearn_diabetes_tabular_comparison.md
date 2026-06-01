# sklearn Diabetes Tabular Regression Comparison

This probe adds a non-FML, non-runtime-only benchmark for the program-search
escalation module. It uses the built-in sklearn diabetes regression dataset and
a multi-split evaluator, avoiding external dataset credentials. The task is
ML-research-like in miniature: a rudimentary predictor must be replaced with a
better tabular regression model.

Lower RMSE is better. The evaluator maximizes negative mean RMSE across five
deterministic splits.

## Results

| Variant | Seeds | Mean RMSE | Mean R2 | Notes |
| --- | ---: | ---: | ---: | --- |
| Initial mean predictor | n/a | 78.572189 | -0.012285 | Rudimentary starting program. |
| Direct DeepSeek rewrite | n/a | 55.895460 | 0.485475 | Recovered a strong Ridge-style baseline. |
| OpenEvolve 3 iter | 0 | 55.895460 | 0.485475 | Matched direct rewrite. |
| OpenEvolve 3 iter | 1 | 55.946535 | 0.484492 | Improved strongly, slightly below direct rewrite. |
| OpenEvolve 3 iter | 2 | 55.895460 | 0.485475 | Matched direct rewrite. |

Across the three OpenEvolve seeds, all runs improved over the initial mean
predictor within three iterations. The median OpenEvolve RMSE was 55.895460,
matching the direct rewrite and improving over the initial baseline by 22.676729
RMSE points. Unlike the MLAgentBench vectorization probe, this task does not
show a clear advantage for program search over direct editing; instead, it shows
that both direct editing and OpenEvolve can quickly recover a standard
supervised-learning baseline when the evaluator is simple and the initial
solution is intentionally weak.

This is therefore evidence for the **coverage and boundary conditions** of the
program-search escalation gate, not evidence that OpenEvolve should always be
preferred. For Co-Pilot AI Scientist v3, the practical policy is to escalate to
program search when the evaluator is automatic and the search space benefits
from iterative exploration, while allowing direct edits when a small, standard
modeling change is likely sufficient.

## Artifact Paths

- Task: `sklearn_diabetes_tabular_task/`
- Direct rewrite: `sklearn_diabetes_direct_deepseek_dummy/`
- OpenEvolve seed 0: `sklearn_diabetes_openevolve_3iter_dummy_seed0/`
- OpenEvolve seed 1: `sklearn_diabetes_openevolve_3iter_dummy_seed1/`
- OpenEvolve seed 2: `sklearn_diabetes_openevolve_3iter_dummy_seed2/`
- Aggregate summary: `sklearn_diabetes_tabular_summary.json`

## Setup Note

This probe was selected after the official MLAgentBench `house-price` setup was
blocked by missing Kaggle tooling/authentication on the Ubuntu host. It should
not be reported as an official MLAgentBench score.
