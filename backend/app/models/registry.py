"""
Model registry for loading and managing model bundles
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import joblib
import numpy as np


class ModelBundle:
    """Container for model, calibration, and metadata"""
    
    def __init__(self, bundle_path: str):
        self.bundle_path = Path(bundle_path)
        self.model = None
        self.calibration = None
        self.training_ranges = None
        self.feature_order = None
        self.surrogate = None
        
        if self.bundle_path.exists():
            self._load_bundle()
        else:
            print(f"Warning: Model bundle not found at {bundle_path}. Using dummy model.")
            self._create_dummy()
    
    def _load_bundle(self):
        """Load model components from bundle directory"""
        # TODO: Load actual booster, calibration, ranges
        # For now, create dummy components
        self._create_dummy()
    
    def _create_dummy(self):
        """Create dummy model for testing"""
        self.model = lambda x: np.random.rand(len(x)) * 0.3  # Dummy predictions
        self.calibration = {"method": "none"}
        self.training_ranges = {
            "wind_speed_10m": [0, 30],
            "rh": [0, 100],
            "rain_24h": [0, 100],
            "gust_10m": [0, 50],
            "t2m": [250, 320],
            "vpd": [0, 8]
        }
        self.feature_order = [
            "wind_speed_10m", "rh", "rain_24h", "gust_10m",
            "t2m", "dewpoint", "vpd", "wind_dir_sin", "wind_dir_cos"
        ]
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Predict probabilities"""
        raw_preds = self.model(features)
        # Apply calibration
        # TODO: Apply actual calibration map
        return raw_preds
    
    def predict_with_ci(self, features: np.ndarray, alpha: float = 0.1) -> tuple:
        """Predict with confidence intervals"""
        preds = self.predict(features)
        # TODO: Compute actual confidence intervals
        ci_lower = np.maximum(0, preds - 0.1)
        ci_upper = np.minimum(1, preds + 0.1)
        return preds, ci_lower, ci_upper


class ModelRegistry:
    """Registry for managing model bundles"""
    
    def __init__(self):
        self._bundles: Dict[str, ModelBundle] = {}
    
    def get_bundle(self, name: str = "default", bundle_path: Optional[str] = None) -> ModelBundle:
        """Get or create model bundle"""
        if name not in self._bundles:
            if bundle_path is None:
                bundle_path = os.environ.get(
                    "MODEL_BUNDLE_PATH",
                    "/backend/models/bundles/model_bundle"
                )
            self._bundles[name] = ModelBundle(bundle_path)
        return self._bundles[name]
    
    def load_surrogate(self, path: Optional[str] = None) -> Any:
        """Load surrogate model for fast counterfactuals"""
        if path is None:
            path = os.environ.get(
                "MODEL_BUNDLE_PATH",
                "/backend/models/bundles/model_bundle"
            )
        surrogate_path = Path(path) / "surrogate.joblib"
        
        if surrogate_path.exists():
            return joblib.load(surrogate_path)
        else:
            # Return dummy surrogate
            return lambda x: np.random.rand(len(x)) * 0.3
