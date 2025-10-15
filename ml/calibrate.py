"""
Model calibration - Platt scaling and Isotonic regression per region
"""
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
import json
from pathlib import Path
from typing import Dict, Any


class PlattScaler:
    """Platt scaling calibration"""
    
    def __init__(self):
        self.model = LogisticRegression()
    
    def fit(self, probas: np.ndarray, y_true: np.ndarray):
        """Fit Platt scaler"""
        probas = probas.reshape(-1, 1)
        self.model.fit(probas, y_true)
    
    def transform(self, probas: np.ndarray) -> np.ndarray:
        """Apply Platt scaling"""
        probas = probas.reshape(-1, 1)
        return self.model.predict_proba(probas)[:, 1]


class IsotonicCalibrator:
    """Isotonic regression calibration"""
    
    def __init__(self):
        self.model = IsotonicRegression(out_of_bounds='clip')
    
    def fit(self, probas: np.ndarray, y_true: np.ndarray):
        """Fit isotonic calibrator"""
        self.model.fit(probas, y_true)
    
    def transform(self, probas: np.ndarray) -> np.ndarray:
        """Apply isotonic calibration"""
        return self.model.predict(probas)


def calibrate_per_region(
    probas: np.ndarray,
    y_true: np.ndarray,
    regions: np.ndarray,
    method: str = 'isotonic'
) -> Dict[int, Any]:
    """
    Calibrate model per region.
    
    Args:
        probas: Raw model probabilities
        y_true: True labels
        regions: Region IDs
        method: 'platt' or 'isotonic'
    
    Returns:
        Dictionary mapping region ID to calibrator
    """
    calibrators = {}
    
    unique_regions = np.unique(regions)
    
    for region_id in unique_regions:
        mask = regions == region_id
        region_probas = probas[mask]
        region_y = y_true[mask]
        
        if method == 'platt':
            calibrator = PlattScaler()
        else:
            calibrator = IsotonicCalibrator()
        
        calibrator.fit(region_probas, region_y)
        calibrators[int(region_id)] = calibrator
        
        print(f"Calibrated region {region_id} ({len(region_probas)} samples)")
    
    return calibrators


def compute_reliability_curve(
    probas: np.ndarray,
    y_true: np.ndarray,
    n_bins: int = 10
) -> tuple:
    """
    Compute reliability (calibration) curve.
    
    Args:
        probas: Predicted probabilities
        y_true: True labels
        n_bins: Number of bins
    
    Returns:
        Tuple of (bin_edges, bin_probas, bin_observed, bin_counts)
    """
    # Create bins
    bin_edges = np.linspace(0, 1, n_bins + 1)
    
    bin_probas = []
    bin_observed = []
    bin_counts = []
    
    for i in range(n_bins):
        mask = (probas >= bin_edges[i]) & (probas < bin_edges[i + 1])
        
        if i == n_bins - 1:  # Include upper bound in last bin
            mask = (probas >= bin_edges[i]) & (probas <= bin_edges[i + 1])
        
        if mask.sum() > 0:
            bin_probas.append(probas[mask].mean())
            bin_observed.append(y_true[mask].mean())
            bin_counts.append(mask.sum())
        else:
            bin_probas.append(np.nan)
            bin_observed.append(np.nan)
            bin_counts.append(0)
    
    return bin_edges, bin_probas, bin_observed, bin_counts


def save_calibration(calibrators: Dict[int, Any], output_path: str):
    """
    Save calibration parameters to JSON.
    
    Args:
        calibrators: Dictionary of calibrators per region
        output_path: Path to save JSON
    """
    calibration_data = {
        'method': 'isotonic',
        'regions': {}
    }
    
    for region_id, calibrator in calibrators.items():
        if isinstance(calibrator, IsotonicCalibrator):
            calibration_data['regions'][str(region_id)] = {
                'x': calibrator.model.X_thresholds_.tolist(),
                'y': calibrator.model.y_thresholds_.tolist()
            }
        elif isinstance(calibrator, PlattScaler):
            calibration_data['regions'][str(region_id)] = {
                'coef': calibrator.model.coef_.tolist(),
                'intercept': calibrator.model.intercept_.tolist()
            }
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(calibration_data, f, indent=2)
    
    print(f"Saved calibration to {output_path}")


if __name__ == "__main__":
    print("Calibration Script")
    
    # Example with synthetic data
    n_samples = 5000
    probas = np.random.beta(2, 5, n_samples)  # Skewed probabilities
    y_true = (np.random.rand(n_samples) < probas * 1.2).astype(int)  # Slightly miscalibrated
    regions = np.random.choice([0, 1, 2], n_samples)
    
    print(f"Mean predicted: {probas.mean():.3f}")
    print(f"Mean observed: {y_true.mean():.3f}")
    
    # Calibrate per region
    print("\nCalibrating per region...")
    calibrators = calibrate_per_region(probas, y_true, regions, method='isotonic')
    
    # Compute reliability curve
    bin_edges, bin_probas, bin_observed, bin_counts = compute_reliability_curve(
        probas, y_true, n_bins=10
    )
    
    print("\nReliability curve:")
    for i in range(len(bin_probas)):
        if not np.isnan(bin_probas[i]):
            print(f"  Bin {i}: pred={bin_probas[i]:.3f}, obs={bin_observed[i]:.3f}, n={bin_counts[i]}")
    
    # Save
    save_calibration(calibrators, '/tmp/calibration.json')
    
    print("\nCalibration complete!")
