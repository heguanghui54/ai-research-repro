import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


def train_and_predict(X_train, y_train, X_eval):
    """Train a Ridge regression model with feature scaling and return predictions."""
    # Handle potential NaN values in training data
    X_train_clean = np.nan_to_num(X_train, nan=0.0)
    y_train_clean = np.nan_to_num(y_train, nan=np.nanmean(y_train))
    X_eval_clean = np.nan_to_num(X_eval, nan=0.0)
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_clean)
    X_eval_scaled = scaler.transform(X_eval_clean)
    
    # Train Ridge regression with cross-validation-inspired alpha
    # Use a moderate regularization to balance bias and variance
    model = Ridge(alpha=1.0, random_state=42)
    model.fit(X_train_scaled, y_train_clean)
    
    # Make predictions
    predictions = model.predict(X_eval_scaled)
    
    # Clip predictions to reasonable range based on training data
    y_min, y_max = np.min(y_train_clean), np.max(y_train_clean)
    predictions = np.clip(predictions, y_min, y_max)
    
    return predictions
