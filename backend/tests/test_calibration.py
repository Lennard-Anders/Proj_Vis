"""
Tests for calibration and reliability
"""
import numpy as np
from app.models.registry import ModelBundle


def test_calibration_exists():
    """Test that calibration data is loaded"""
    bundle = ModelBundle("/backend/models/bundles/model_bundle")
    assert bundle.calibration is not None


def test_prediction_in_range():
    """Test that predictions are in valid range [0, 1]"""
    bundle = ModelBundle("/backend/models/bundles/model_bundle")
    
    # Create dummy features
    features = np.random.rand(10, 9)
    
    # Predict
    preds = bundle.predict(features)
    
    # Check range
    assert np.all(preds >= 0)
    assert np.all(preds <= 1)


def test_confidence_intervals():
    """Test that confidence intervals are valid"""
    bundle = ModelBundle("/backend/models/bundles/model_bundle")
    
    features = np.random.rand(10, 9)
    
    preds, ci_lower, ci_upper = bundle.predict_with_ci(features)
    
    # Check that CI bounds are valid
    assert np.all(ci_lower <= preds)
    assert np.all(preds <= ci_upper)
    assert np.all(ci_lower >= 0)
    assert np.all(ci_upper <= 1)
