import numpy as np

class FairnessAlgorithm:
    def fit(self, X, y, sensitive_features=None):
        self.classes_ = np.array([0, 1])
        return self

    def predict(self, X):
        return np.zeros(len(X), dtype=int)

    def predict_proba(self, X):
        proba = np.zeros((len(X), 2), dtype=float)
        proba[:, 0] = 1.0
        return proba
