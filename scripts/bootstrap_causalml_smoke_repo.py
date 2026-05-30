#!/usr/bin/env python3
"""Bootstrap a minimal causalml-style workspace for FML-bench smoke tests.

The official FML-bench task configuration expects a git repo at
`workspace/Causality_causalml/causalml` with a small package surface:

- causalml.inference.tf.DragonNet
- causalml.metrics.get_cumgain / auuc_score
- causalml.propensity.ElasticNetPropensityModel

The upstream GitHub clone can be slow or flaky in some environments, so this
script creates a lightweight, deterministic local stand-in that is sufficient
for the benchmark smoke test.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import shutil
import subprocess
from pathlib import Path

import numpy as np


DRAGONNET_PY = """from __future__ import annotations

import numpy as np
from sklearn.linear_model import LinearRegression


class DragonNet:
    def __init__(self, neurons_per_layer=200, val_split=0.3, targeted_reg=True):
        self.model_treat = LinearRegression()
        self.model_control = LinearRegression()
        self.fitted = False

    def fit(self, X, treatment, y):
        X = np.asarray(X)
        treatment = np.asarray(treatment).reshape(-1)
        y = np.asarray(y).reshape(-1)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self.model_treat.fit(X[treatment == 1], y[treatment == 1] if np.any(treatment == 1) else y)
        self.model_control.fit(X[treatment == 0], y[treatment == 0] if np.any(treatment == 0) else y)
        self.fitted = True
        return self

    def predict_tau(self, X):
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if not self.fitted:
            raise RuntimeError("DragonNet must be fitted before predicting.")
        treat = self.model_treat.predict(X)
        control = self.model_control.predict(X)
        return (treat - control).reshape(-1, 1)
"""


UTILS_PY = """from __future__ import annotations

import numpy as np


def normalize(a):
    a = np.asarray(a, dtype=float)
    total = a.sum()
    if total == 0:
        return np.ones_like(a) / max(len(a), 1)
    return a / total
"""


METRICS_PY = """from __future__ import annotations

import numpy as np
import pandas as pd


def auuc_score(df_preds):
    # Very small, deterministic proxy for the real metric.
    # Returns a pandas Series so .iloc[0] works in the benchmark script.
    if isinstance(df_preds, pd.DataFrame):
        values = df_preds.iloc[:, 0].to_numpy(dtype=float)
        target = df_preds.iloc[:, 1].to_numpy(dtype=float)
    else:
        values = np.asarray(df_preds)[:, 0].astype(float)
        target = np.asarray(df_preds)[:, 1].astype(float)
    score = float(np.mean(np.abs(values - target)))
    return pd.Series([score], index=["auuc"])


def get_cumgain(df_preds):
    # Return a simple cumulative gain curve proxy.
    if not isinstance(df_preds, pd.DataFrame):
        df_preds = pd.DataFrame(df_preds)
    cum = df_preds.cumsum()
    return cum
"""


PROPENSITY_PY = """from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression


class ElasticNetPropensityModel:
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)

    def fit_predict(self, X, treatment):
        X = np.asarray(X)
        treatment = np.asarray(treatment).reshape(-1)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        self.model.fit(X, treatment)
        return self.model.predict_proba(X)[:, 1]
"""


INIT_PY = """from .dragonnet import DragonNet
"""


TF_INIT_PY = """from .dragonnet import DragonNet
"""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def generate_ihdp_csv(path: Path, n: int = 256, seed: int = 42) -> None:
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        x = rng.normal(size=25)
        treatment = int(rng.integers(0, 2))
        mu0 = float(rng.normal())
        mu1 = mu0 + float(rng.normal(loc=0.5, scale=0.2))
        y_factual = float(mu1 if treatment else mu0) + float(rng.normal(scale=0.1))
        y_cfactual = float(mu0 if treatment else mu1) + float(rng.normal(scale=0.1))
        row = [treatment, y_factual, y_cfactual, mu0, mu1, *x.tolist()]
        rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Target workspace repo root")
    args = parser.parse_args()

    repo = Path(args.repo)
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True, exist_ok=True)

    # Minimal package surface expected by the benchmark.
    write_file(repo / "causalml" / "__init__.py", "from .inference.tf import DragonNet\n")
    write_file(repo / "causalml" / "inference" / "__init__.py", "")
    write_file(repo / "causalml" / "inference" / "tf" / "__init__.py", TF_INIT_PY)
    write_file(repo / "causalml" / "inference" / "tf" / "dragonnet.py", DRAGONNET_PY)
    write_file(repo / "causalml" / "inference" / "tf" / "utils.py", UTILS_PY)
    write_file(repo / "causalml" / "metrics.py", METRICS_PY)
    write_file(repo / "causalml" / "propensity.py", PROPENSITY_PY)

    # Minimal docs/data path expected by train.py.
    generate_ihdp_csv(repo / "docs" / "examples" / "data" / "ihdp_npci_3.csv")

    # The benchmark copies this file into the repo root before each run.
    split_cfg = {"val_ratio": 0.114, "val_seed": 42}
    write_file(repo / "split_config.json", json.dumps(split_cfg, indent=2) + "\n")

    # Make it a git repo so the benchmark's backup logic is satisfied.
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(
        ["git", "commit", "-m", "bootstrap minimal causalml smoke repo", "--allow-empty"],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Bootstrapped minimal repo at {repo}")


if __name__ == "__main__":
    main()
