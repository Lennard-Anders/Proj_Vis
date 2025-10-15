"""
Model loader service for loading and managing the trained model bundle
"""
import pickle
import os
from typing import Any


class MockModel:
    """Mock model for initial setup"""
    
    def predict(self, X):
        """Simple mock prediction"""
        import numpy as np
        # Return random predictions for now
        return np.random.random(len(X)) * 0.8 + 0.1


_model_instance = None
_model_path = os.getenv("MODEL_PATH", "/models/wildfire_model.pkl")


def load_model_bundle(model_path: str = None) -> Any:
    """
    Load the trained model bundle from disk
    
    Args:
        model_path: Path to the model file
        
    Returns:
        Loaded model object
    """
    global _model_instance
    
    path = model_path or _model_path
    
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                _model_instance = pickle.load(f)
        else:
            # Use mock model if real model not available
            _model_instance = MockModel()
    except Exception as e:
        print(f"Warning: Could not load model from {path}: {e}")
        _model_instance = MockModel()
    
    return _model_instance


def get_model() -> Any:
    """
    Get the loaded model instance (singleton pattern)
    
    Returns:
        Model instance
    """
    global _model_instance
    
    if _model_instance is None:
        _model_instance = load_model_bundle()
    
    return _model_instance


def reload_model():
    """
    Force reload of the model from disk
    """
    global _model_instance
    _model_instance = None
    return load_model_bundle()
