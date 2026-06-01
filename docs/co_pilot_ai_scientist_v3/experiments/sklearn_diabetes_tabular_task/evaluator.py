import importlib.util
import math
import time

import numpy as np
from sklearn.datasets import load_diabetes
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def load_program(path):
    spec = importlib.util.spec_from_file_location("candidate_program", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _rmse(y_true, y_pred):
    return math.sqrt(mean_squared_error(y_true, y_pred))


def evaluate(path):
    try:
        module = load_program(path)
        if not hasattr(module, "train_and_predict"):
            return {"combined_score": -1e9, "score": -1e9, "error": "missing train_and_predict"}

        data = load_diabetes()
        X = data.data.astype(np.float64)
        y = data.target.astype(np.float64)

        rmses = []
        maes = []
        r2s = []
        elapsed = []
        seeds = [3, 11, 23, 37, 53]
        for seed in seeds:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.25, random_state=seed
            )
            start = time.perf_counter()
            pred = module.train_and_predict(X_train, y_train, X_test)
            elapsed.append(time.perf_counter() - start)
            pred = np.asarray(pred, dtype=np.float64).reshape(-1)
            if pred.shape != y_test.shape or not np.all(np.isfinite(pred)):
                return {
                    "combined_score": -1e9,
                    "score": -1e9,
                    "error": "invalid prediction shape or non-finite predictions",
                }
            rmses.append(_rmse(y_test, pred))
            maes.append(mean_absolute_error(y_test, pred))
            r2s.append(r2_score(y_test, pred))

        mean_rmse = float(np.mean(rmses))
        std_rmse = float(np.std(rmses))
        mean_mae = float(np.mean(maes))
        mean_r2 = float(np.mean(r2s))
        mean_elapsed = float(np.mean(elapsed))

        # Maximize negative RMSE. Add only a tiny time penalty to break ties while
        # keeping predictive quality dominant.
        score = -mean_rmse - 0.01 * mean_elapsed
        return {
            "combined_score": float(score),
            "score": float(score),
            "mean_rmse": mean_rmse,
            "std_rmse": std_rmse,
            "mean_mae": mean_mae,
            "mean_r2": mean_r2,
            "mean_elapsed_seconds": mean_elapsed,
            "splits": len(seeds),
        }
    except Exception as exc:
        return {
            "combined_score": -1e9,
            "score": -1e9,
            "error": type(exc).__name__ + ": " + str(exc)[:300],
        }
