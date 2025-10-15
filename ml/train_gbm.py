"""
Train gradient boosting model with monotonicity constraints
"""
import numpy as np
import pandas as pd
import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path


def load_training_data(path: str) -> tuple:
    """
    Load training data from Parquet.
    
    Args:
        path: Path to Parquet file or directory
    
    Returns:
        Tuple of (X, y, feature_names)
    """
    df = pd.read_parquet(path)
    
    # Feature columns
    feature_cols = [
        'wind_speed_10m', 'wind_dir_sin', 'wind_dir_cos',
        'gust_10m', 't2m', 'dewpoint', 'rh', 'vpd',
        'rain_24h', 'rain_72h', 'recent_fires_72h_20km',
        'month', 'clim_mean', 'clim_amp'
    ]
    
    # Filter to available columns
    feature_cols = [col for col in feature_cols if col in df.columns]
    
    X = df[feature_cols].values
    y = df['ignition'].values if 'ignition' in df.columns else np.zeros(len(df))
    
    return X, y, feature_cols


def train_lightgbm(
    X_train, y_train,
    X_val, y_val,
    monotone_constraints: dict = None
) -> lgb.Booster:
    """
    Train LightGBM with monotonicity constraints.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        monotone_constraints: Dict mapping feature index to constraint (-1, 0, 1)
    
    Returns:
        Trained LightGBM booster
    """
    # Default monotone constraints
    if monotone_constraints is None:
        # Indices correspond to feature order
        # wind_speed_10m: +1 (higher wind = higher risk)
        # rh: -1 (higher humidity = lower risk)
        # rain_24h: -1 (more rain = lower risk)
        monotone_constraints = {
            0: 1,   # wind_speed_10m
            6: -1,  # rh
            8: -1,  # rain_24h
            9: -1,  # rain_72h
        }
    
    # Convert to LightGBM format
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    # Parameters
    params = {
        'objective': 'binary',
        'metric': 'auc',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': 0,
        'monotone_constraints': list(monotone_constraints.values()) if monotone_constraints else None
    }
    
    # Train
    booster = lgb.train(
        params,
        train_data,
        num_boost_round=1000,
        valid_sets=[train_data, val_data],
        valid_names=['train', 'val'],
        callbacks=[
            lgb.early_stopping(stopping_rounds=50),
            lgb.log_evaluation(period=100)
        ]
    )
    
    return booster


def train_xgboost(
    X_train, y_train,
    X_val, y_val,
    monotone_constraints: tuple = None
) -> xgb.Booster:
    """
    Train XGBoost with monotonicity constraints.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        monotone_constraints: Tuple of constraints per feature
    
    Returns:
        Trained XGBoost booster
    """
    # Default monotone constraints
    if monotone_constraints is None:
        monotone_constraints = (1, 0, 0, 0, 0, 0, -1, 0, -1, -1, 0, 0, 0, 0)
    
    # Convert to DMatrix
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    
    # Parameters
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'max_depth': 6,
        'eta': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'monotone_constraints': monotone_constraints
    }
    
    # Train
    evals = [(dtrain, 'train'), (dval, 'val')]
    booster = xgb.train(
        params,
        dtrain,
        num_boost_round=1000,
        evals=evals,
        early_stopping_rounds=50,
        verbose_eval=100
    )
    
    return booster


def save_model(booster, output_dir: str, model_type: str = 'lightgbm'):
    """
    Save trained model.
    
    Args:
        booster: Trained booster
        output_dir: Output directory
        model_type: 'lightgbm' or 'xgboost'
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if model_type == 'lightgbm':
        booster.save_model(str(output_path / 'booster.txt'))
    elif model_type == 'xgboost':
        booster.save_model(str(output_path / 'booster.json'))
    
    print(f"Saved {model_type} model to {output_dir}")


if __name__ == "__main__":
    print("Training Script")
    
    # TODO: Add argparse CLI
    # Example usage with synthetic data
    n_samples = 10000
    n_features = 14
    
    X = np.random.rand(n_samples, n_features)
    y = (X[:, 0] * 0.3 + (1 - X[:, 6]) * 0.3 + np.random.rand(n_samples) * 0.4) > 0.5
    y = y.astype(int)
    
    # Split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Positive rate: {y_train.mean():.3f}")
    
    # Train LightGBM
    print("\nTraining LightGBM...")
    booster = train_lightgbm(X_train, y_train, X_val, y_val)
    
    # Save
    save_model(booster, '/tmp/model_output', model_type='lightgbm')
    
    print("\nTraining complete!")
