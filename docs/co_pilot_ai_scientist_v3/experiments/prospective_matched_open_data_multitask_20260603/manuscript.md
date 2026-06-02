# Open-Data Multi-Task Matched Pilot Manuscript

Run ID: `prospective_matched_open_data_multitask_20260603`

## Question

Can an IGRE evaluator-stress gate improve branch selection on open,
machine-gradeable tasks when both the autonomous and co-pilot selectors use the
same candidate model portfolio and data splits?

## Method

We ran `5` scikit-learn built-in datasets across
`5` stratified split seeds on the SSH Ubuntu host using
the `fmlbench` conda environment, yielding
`25` paired branch-selection
comparisons. For every dataset and split, the two conditions shared the same
train/validation/test split and the same candidate portfolio. The autonomous
selector chose the branch with highest validation accuracy. The co-pilot
condition used an evaluator-stress gate to select by validation balanced
accuracy with a macro-F1 guardrail.

## Results

| Dataset | Splits | Autonomous mean test balanced accuracy | Co-pilot mean test balanced accuracy | Delta | Co/Auto/Tie | Changed selections |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| breast_cancer | 5 | 0.971627 | 0.964087 | -0.007540 | 0/2/3 | 2 |
| wine | 5 | 0.988571 | 0.988571 | 0.000000 | 0/0/5 | 0 |
| digits | 5 | 0.978214 | 0.978214 | 0.000000 | 0/0/5 | 0 |
| digits_zero_vs_rest | 5 | 0.994444 | 0.994444 | 0.000000 | 0/0/5 | 0 |
| synthetic_imbalanced_stress | 5 | 0.691427 | 0.706811 | 0.015385 | 2/0/3 | 2 |

Aggregate mean test balanced accuracy:

- Autonomous accuracy-only selector: `0.924857`
- Co-pilot guardrailed selector: `0.926426`
- Co-pilot minus autonomous: `0.001569`

Dataset-split outcomes: `2` co-pilot wins,
`2` autonomous wins, and
`21` ties. Selection changed in
`4` dataset-split comparisons.

## Claim

This pilot supports a narrow evaluator-design claim: an IGRE gate can be
implemented as a reproducible branch-selection policy on multiple open
machine-gradeable tasks. It does not prove that Co-Pilot AI Scientist v3
outperforms autonomous AI Scientist-v2 on paper-quality or broad benchmark
performance.
