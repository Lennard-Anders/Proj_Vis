"""
Model calibration using isotonic regression and Platt scaling
"""
import numpy as np
import pandas as pd
from typing import Tuple
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
import joblib


class ModelCalibrator:
    """
    Calibrate model predictions to true probabilities
    """
    
    def __init__(self, method: str = "isotonic"):
        """
        Initialize calibrator
        
        Args:
            method: 'isotonic' or 'platt'
        """
        self.method = method
        self.calibrator = None
        
        if method == "isotonic":
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
        elif method == "platt":
            self.calibrator = LogisticRegression()
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def fit(self, y_true: np.ndarray, y_pred: np.ndarray):
        """
        Fit calibrator
        
        Args:
            y_true: True labels
            y_pred: Raw predictions
        """
        if self.method == "isotonic":
            self.calibrator.fit(y_pred, y_true)
        elif self.method == "platt":
            # Platt scaling needs 2D input
            self.calibrator.fit(y_pred.reshape(-1, 1), y_true)
    
    def transform(self, y_pred: np.ndarray) -> np.ndarray:
        """
        Apply calibration
        
        Args:
            y_pred: Raw predictions
            
        Returns:
            Calibrated predictions
        """
        if self.calibrator is None:
            raise ValueError("Calibrator not fitted")
        
        if self.method == "isotonic":
            return self.calibrator.transform(y_pred)
        elif self.method == "platt":
            return self.calibrator.predict_proba(y_pred.reshape(-1, 1))[:, 1]
    
    def fit_transform(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """
        Fit and transform in one step
        
        Args:
            y_true: True labels
            y_pred: Raw predictions
            
        Returns:
            Calibrated predictions
        """
        self.fit(y_true, y_pred)
        return self.transform(y_pred)
    
    def save(self, path: str):
        """Save calibrator"""
        calibrator_data = {
            'method': self.method,
            'calibrator': self.calibrator
        }
        joblib.dump(calibrator_data, path)
    
    @classmethod
    def load(cls, path: str) -> 'ModelCalibrator':
        """Load calibrator"""
        calibrator_data = joblib.load(path)
        instance = cls(method=calibrator_data['method'])
        instance.calibrator = calibrator_data['calibrator']
        return instance


def calculate_calibration_curve(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bins: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate calibration curve (reliability diagram)
    
    Args:
        y_true: True labels
        y_pred: Predicted probabilities
        n_bins: Number of bins
        
    Returns:
        Tuple of (mean predicted probability, fraction of positives) per bin
    """
    bins = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(y_pred, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)
    
    bin_sums = np.bincount(bin_indices, weights=y_pred, minlength=n_bins)
    bin_true = np.bincount(bin_indices, weights=y_true, minlength=n_bins)
    bin_total = np.bincount(bin_indices, minlength=n_bins)
    
    # Avoid division by zero
    nonzero = bin_total != 0
    
    prob_true = np.zeros(n_bins)
    prob_pred = np.zeros(n_bins)
    
    prob_true[nonzero] = bin_true[nonzero] / bin_total[nonzero]
    prob_pred[nonzero] = bin_sums[nonzero] / bin_total[nonzero]
    
    return prob_pred, prob_true


def expected_calibration_error(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bins: int = 10
) -> float:
    """
    Calculate Expected Calibration Error (ECE)
    
    Args:
        y_true: True labels
        y_pred: Predicted probabilities
        n_bins: Number of bins
        
    Returns:
        ECE value
    """
    bins = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(y_pred, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)
    
    bin_total = np.bincount(bin_indices, minlength=n_bins)
    bin_true = np.bincount(bin_indices, weights=y_true, minlength=n_bins)
    bin_pred = np.bincount(bin_indices, weights=y_pred, minlength=n_bins)
    
    nonzero = bin_total != 0
    
    acc = np.zeros(n_bins)
    conf = np.zeros(n_bins)
    
    acc[nonzero] = bin_true[nonzero] / bin_total[nonzero]
    conf[nonzero] = bin_pred[nonzero] / bin_total[nonzero]
    
    ece = np.sum(bin_total[nonzero] * np.abs(acc[nonzero] - conf[nonzero])) / np.sum(bin_total)
    
    return ece


def brier_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Brier score
    
    Args:
        y_true: True labels
        y_pred: Predicted probabilities
        
    Returns:
        Brier score
    """
    return np.mean((y_true - y_pred) ** 2)
