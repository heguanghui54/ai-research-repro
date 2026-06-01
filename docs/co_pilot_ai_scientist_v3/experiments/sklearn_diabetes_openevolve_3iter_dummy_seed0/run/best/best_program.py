import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


def train_and_predict(X_train, y_train, X_eval):
    """Train a Ridge regression model and return predictions for X_eval.
    
    Uses standardization for numerical stability and regularization to prevent overfitting.
    Falls back to mean prediction if model training fails.
    """
    try:
        # Standardize features for better numerical stability
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_eval_scaled = scaler.transform(X_eval)
        
        # Train Ridge regression with cross-validation-like alpha
        model = Ridge(alpha=1.0, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        predictions = model.predict(X_eval_scaled)
        
        # Clip predictions to reasonable range based on training data
        y_min, y_max = np.min(y_train), np.max(y_train)
        predictions = np.clip(predictions, y_min, y_max)
        
        return predictions
    except Exception:
        # Fallback to mean prediction if anything fails
        return np.full(X_eval.shape[0], float(np.mean(y_train)))
