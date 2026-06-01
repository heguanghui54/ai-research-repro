import numpy as np


def train_and_predict(X_train, y_train, X_eval):
    """Return a rudimentary baseline prediction for X_eval."""
    return np.full(X_eval.shape[0], float(np.mean(y_train)))
