"""
Train surrogate model for fast what-if scenarios
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
import joblib
from pathlib import Path


def train_surrogate(X_full: np.ndarray, y: np.ndarray, feature_names: list) -> object:
    """
    Train lightweight surrogate model.
    
    Uses only key features: wind_speed_10m, rh, rain_24h, gust_10m
    
    Args:
        X_full: Full feature matrix
        y: Labels
        feature_names: List of feature names
    
    Returns:
        Trained surrogate model
    """
    # Select key features
    key_features = ['wind_speed_10m', 'rh', 'rain_24h', 'gust_10m']
    key_indices = [i for i, name in enumerate(feature_names) if name in key_features]
    
    X_simple = X_full[:, key_indices]
    
    # Train small GBM
    model = GradientBoostingClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.1,
        random_state=42
    )
    
    model.fit(X_simple, y)
    
    print(f"Trained surrogate on {X_simple.shape[1]} features")
    print(f"Training accuracy: {model.score(X_simple, y):.3f}")
    
    return model


def save_surrogate(model: object, output_path: str):
    """Save surrogate model"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"Saved surrogate to {output_path}")


if __name__ == "__main__":
    print("Surrogate Training Script")
    
    # Synthetic data
    n_samples = 10000
    n_features = 14
    X = np.random.rand(n_samples, n_features)
    y = (X[:, 0] * 0.3 + (1 - X[:, 1]) * 0.3 + np.random.rand(n_samples) * 0.4) > 0.5
    y = y.astype(int)
    
    feature_names = ['wind_speed_10m', 'rh', 'rain_24h', 'gust_10m'] + [f'f{i}' for i in range(10)]
    
    # Train
    surrogate = train_surrogate(X, y, feature_names)
    
    # Save
    save_surrogate(surrogate, '/tmp/surrogate.joblib')
    
    print("\nSurrogate training complete!")
