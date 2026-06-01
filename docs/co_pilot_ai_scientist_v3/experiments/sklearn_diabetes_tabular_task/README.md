# sklearn Diabetes Tabular Regression Task

This controlled non-FML task tests whether the program-search escalation module
can improve a small machine-learning modeling subproblem rather than only a
runtime optimization subproblem.

The task uses the built-in `sklearn.datasets.load_diabetes` regression dataset,
so it does not require Kaggle credentials or network downloads. Candidate
programs must expose:

```python
def train_and_predict(X_train, y_train, X_eval):
    ...
```

The evaluator runs multiple deterministic train/test splits and maximizes
negative RMSE. Lower `mean_rmse` is better; higher `score` is better.

This is not claimed as an official MLAgentBench score. It is a controlled,
reproducible tabular-regression probe selected after MLAgentBench `house-price`
setup was blocked by Kaggle tooling/authentication.
