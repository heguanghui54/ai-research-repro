# Open-Data Multi-Task Matched Pilot Manuscript

Run ID: `prospective_matched_open_data_multitask_20260603`

## Question

Can an IGRE evaluator-stress gate improve branch selection on open,
machine-gradeable tasks when both the autonomous and co-pilot selectors use the
same candidate model portfolio and data splits?

## Method

We ran `5` scikit-learn built-in datasets on the SSH
Ubuntu host using the `fmlbench` conda environment. For every dataset, the two
conditions shared the same train/validation/test split and the same candidate
portfolio. The autonomous selector chose the branch with highest validation
accuracy. The co-pilot condition used an evaluator-stress gate to select by
validation balanced accuracy with a macro-F1 guardrail.

## Results

| Dataset | Autonomous branch | Autonomous test balanced accuracy | Co-pilot branch | Co-pilot test balanced accuracy | Delta |
| --- | --- | ---: | --- | ---: | ---: |
| breast_cancer | logreg_standardized | 0.958074 | logreg_standardized | 0.958074 | 0.000000 |
| wine | random_forest | 1.000000 | random_forest | 1.000000 | 0.000000 |
| digits | svc_rbf_standardized | 0.983400 | svc_rbf_standardized | 0.983400 | 0.000000 |
| digits_zero_vs_rest | knn_standardized | 1.000000 | knn_standardized | 1.000000 | 0.000000 |
| synthetic_imbalanced_stress | svc_rbf_standardized | 0.653846 | svc_rbf_balanced_standardized | 0.728567 | 0.074720 |

Aggregate mean test balanced accuracy:

- Autonomous accuracy-only selector: `0.919064`
- Co-pilot guardrailed selector: `0.934008`
- Co-pilot minus autonomous: `0.014944`

Dataset outcomes: `1` co-pilot wins,
`0` autonomous wins, and
`4` ties. Selection changed in
`1` datasets.

## Claim

This pilot supports a narrow evaluator-design claim: an IGRE gate can be
implemented as a reproducible branch-selection policy on multiple open
machine-gradeable tasks. It does not prove that Co-Pilot AI Scientist v3
outperforms autonomous AI Scientist-v2 on paper-quality or broad benchmark
performance.
