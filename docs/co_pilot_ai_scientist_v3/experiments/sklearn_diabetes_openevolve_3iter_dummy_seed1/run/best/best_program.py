import numpy as np


def train_and_predict(X_train, y_train, X_eval):
    """Train a linear regression model and predict on X_eval."""
    # Add bias term (intercept) to feature matrix
    X_train_bias = np.c_[np.ones(X_train.shape[0]), X_train]
    X_eval_bias = np.c_[np.ones(X_eval.shape[0]), X_eval]
    
    # Solve normal equations: theta = (X^T X)^(-1) X^T y
    # Using pseudo-inverse for numerical stability
    theta = np.linalg.pinv(X_train_bias.T @ X_train_bias) @ X_train_bias.T @ y_train
    
    # Make predictions
    predictions = X_eval_bias @ theta
    
    return predictions
