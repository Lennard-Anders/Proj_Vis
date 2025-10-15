"""
Surrogate model for fast inference
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
import joblib


class SurrogateModel:
    """
    Fast surrogate model for real-time inference
    Approximates complex physics-based or ML models
    """
    
    def __init__(self, model_type: str = "mlp"):
        """
        Initialize surrogate model
        
        Args:
            model_type: 'mlp' or 'rf' (random forest)
        """
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        
        if model_type == "mlp":
            self.model = MLPRegressor(
                hidden_layer_sizes=(64, 32, 16),
                activation='relu',
                max_iter=500,
                random_state=42
            )
        elif model_type == "rf":
            self.model = RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        X_val: pd.DataFrame = None,
        y_val: np.ndarray = None
    ) -> Dict[str, float]:
        """
        Train surrogate model
        
        Args:
            X_train: Training features
            y_train: Training targets (from complex model)
            X_val: Validation features
            y_val: Validation targets
            
        Returns:
            Training metrics
        """
        self.feature_names = list(X_train.columns)
        
        # Train
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        train_rmse = np.sqrt(np.mean((y_train - train_pred) ** 2))
        
        metrics = {
            'train_rmse': train_rmse,
            'train_mae': np.mean(np.abs(y_train - train_pred))
        }
        
        if X_val is not None and y_val is not None:
            val_pred = self.model.predict(X_val)
            metrics['val_rmse'] = np.sqrt(np.mean((y_val - val_pred) ** 2))
            metrics['val_mae'] = np.mean(np.abs(y_val - val_pred))
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features
            
        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        return self.model.predict(X)
    
    def save(self, path: str):
        """Save surrogate model"""
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, path)
    
    @classmethod
    def load(cls, path: str) -> 'SurrogateModel':
        """Load surrogate model"""
        model_data = joblib.load(path)
        instance = cls(model_type=model_data['model_type'])
        instance.model = model_data['model']
        instance.feature_names = model_data['feature_names']
        return instance


def create_surrogate_from_model(
    base_model,
    X_sample: pd.DataFrame,
    model_type: str = "mlp"
) -> SurrogateModel:
    """
    Create surrogate model by distilling knowledge from base model
    
    Args:
        base_model: Complex model to approximate
        X_sample: Sample data for distillation
        model_type: Type of surrogate model
        
    Returns:
        Trained surrogate model
    """
    # Generate targets from base model
    if hasattr(base_model, 'predict'):
        y_sample = base_model.predict(X_sample)
    else:
        raise ValueError("Base model must have predict method")
    
    # Train surrogate
    surrogate = SurrogateModel(model_type=model_type)
    metrics = surrogate.train(X_sample, y_sample)
    
    print(f"Surrogate model trained with RMSE: {metrics['train_rmse']:.4f}")
    
    return surrogate


def benchmark_surrogate(
    surrogate_model: SurrogateModel,
    base_model,
    X_test: pd.DataFrame
) -> Dict[str, float]:
    """
    Benchmark surrogate vs base model
    
    Args:
        surrogate_model: Surrogate model
        base_model: Base model
        X_test: Test data
        
    Returns:
        Benchmark metrics
    """
    import time
    
    # Surrogate predictions
    start = time.time()
    surrogate_preds = surrogate_model.predict(X_test)
    surrogate_time = time.time() - start
    
    # Base model predictions
    start = time.time()
    if hasattr(base_model, 'predict'):
        base_preds = base_model.predict(X_test)
    else:
        raise ValueError("Base model must have predict method")
    base_time = time.time() - start
    
    # Compute agreement
    agreement_rmse = np.sqrt(np.mean((base_preds - surrogate_preds) ** 2))
    agreement_mae = np.mean(np.abs(base_preds - surrogate_preds))
    correlation = np.corrcoef(base_preds, surrogate_preds)[0, 1]
    
    return {
        'agreement_rmse': agreement_rmse,
        'agreement_mae': agreement_mae,
        'correlation': correlation,
        'speedup': base_time / surrogate_time,
        'surrogate_time': surrogate_time,
        'base_time': base_time
    }
