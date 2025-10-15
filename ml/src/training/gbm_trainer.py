"""
Gradient Boosting Machine training with monotone constraints
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import joblib


class MonotoneGBM:
    """
    Gradient Boosting Machine with monotone constraints for wildfire risk
    """
    
    def __init__(
        self,
        model_type: str = "xgboost",
        monotone_constraints: Optional[Dict[str, int]] = None
    ):
        """
        Initialize GBM with monotone constraints
        
        Args:
            model_type: 'xgboost' or 'lightgbm'
            monotone_constraints: Dictionary of feature -> constraint (1, 0, -1)
        """
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        
        # Default monotone constraints for wildfire risk
        if monotone_constraints is None:
            self.monotone_constraints = {
                'temperature': 1,        # Higher temp increases risk
                'humidity': -1,          # Higher humidity decreases risk
                'wind_speed': 1,         # Higher wind increases risk
                'precipitation': -1,     # More rain decreases risk
                'fuel_moisture': -1,     # More moisture decreases risk
                'drought_index': 1,      # Higher drought increases risk
                'vpd': 1                 # Higher VPD increases risk
            }
        else:
            self.monotone_constraints = monotone_constraints
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        validation_split: float = 0.2,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Train the GBM model
        
        Args:
            X: Training features
            y: Training labels
            validation_split: Fraction for validation
            params: Additional model parameters
            
        Returns:
            Training history
        """
        self.feature_names = list(X.columns)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42
        )
        
        # Prepare monotone constraint vector
        monotone_vector = [
            self.monotone_constraints.get(feat, 0) 
            for feat in self.feature_names
        ]
        
        if self.model_type == "xgboost":
            self.model = self._train_xgboost(
                X_train, y_train, X_val, y_val, monotone_vector, params
            )
        elif self.model_type == "lightgbm":
            self.model = self._train_lightgbm(
                X_train, y_train, X_val, y_val, monotone_vector, params
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Evaluate
        train_preds = self.predict(X_train)
        val_preds = self.predict(X_val)
        
        history = {
            'train_rmse': np.sqrt(np.mean((y_train - train_preds) ** 2)),
            'val_rmse': np.sqrt(np.mean((y_val - val_preds) ** 2)),
            'train_mae': np.mean(np.abs(y_train - train_preds)),
            'val_mae': np.mean(np.abs(y_val - val_preds))
        }
        
        return history
    
    def _train_xgboost(
        self,
        X_train, y_train, X_val, y_val,
        monotone_vector, params
    ) -> xgb.Booster:
        """Train XGBoost model"""
        default_params = {
            'objective': 'reg:squarederror',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'monotone_constraints': tuple(monotone_vector),
            'random_state': 42
        }
        
        if params:
            default_params.update(params)
        
        # Separate out XGBoost-specific params
        n_estimators = default_params.pop('n_estimators', 100)
        
        dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=self.feature_names)
        dval = xgb.DMatrix(X_val, label=y_val, feature_names=self.feature_names)
        
        evals = [(dtrain, 'train'), (dval, 'val')]
        
        model = xgb.train(
            default_params,
            dtrain,
            num_boost_round=n_estimators,
            evals=evals,
            early_stopping_rounds=10,
            verbose_eval=False
        )
        
        return model
    
    def _train_lightgbm(
        self,
        X_train, y_train, X_val, y_val,
        monotone_vector, params
    ) -> lgb.Booster:
        """Train LightGBM model"""
        default_params = {
            'objective': 'regression',
            'metric': 'rmse',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'monotone_constraints': monotone_vector,
            'random_state': 42,
            'verbose': -1
        }
        
        if params:
            default_params.update(params)
        
        n_estimators = default_params.pop('n_estimators', 100)
        
        train_data = lgb.Dataset(X_train, label=y_train, feature_name=self.feature_names)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data, feature_name=self.feature_names)
        
        model = lgb.train(
            default_params,
            train_data,
            num_boost_round=n_estimators,
            valid_sets=[train_data, val_data],
            valid_names=['train', 'val'],
            callbacks=[lgb.early_stopping(10), lgb.log_evaluation(period=0)]
        )
        
        return model
    
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
        
        if self.model_type == "xgboost":
            dtest = xgb.DMatrix(X, feature_names=self.feature_names)
            return self.model.predict(dtest)
        else:
            return self.model.predict(X)
    
    def save(self, path: str):
        """Save model to disk"""
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'monotone_constraints': self.monotone_constraints
        }
        joblib.dump(model_data, path)
    
    @classmethod
    def load(cls, path: str) -> 'MonotoneGBM':
        """Load model from disk"""
        model_data = joblib.load(path)
        
        instance = cls(
            model_type=model_data['model_type'],
            monotone_constraints=model_data['monotone_constraints']
        )
        instance.model = model_data['model']
        instance.feature_names = model_data['feature_names']
        
        return instance
