"""
Counterfactual service - full re-score and surrogate path
"""
from typing import Dict, List
import numpy as np

from app.models.schemas import FeatureDelta, ReasonCodeDelta
from app.models.registry import ModelRegistry


class CounterfactualService:
    """Service for counterfactual what-if analysis"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.bundle = registry.get_bundle()
        self.surrogate = registry.load_surrogate()
    
    def primary_full_rescore(
        self,
        lat: float,
        lon: float,
        date: str,
        deltas: FeatureDelta
    ) -> Dict:
        """
        Full model re-scoring with modified features.
        
        TODO: Load actual baseline features and apply deltas
        TODO: Run full model inference
        """
        # Get baseline features
        baseline_features = self._get_baseline_features(lat, lon, date)
        
        # Apply deltas
        modified_features = self._apply_deltas(baseline_features, deltas)
        
        # Predict baseline and modified
        baseline_prob = self.bundle.predict(baseline_features)[0]
        modified_prob = self.bundle.predict(modified_features)[0]
        
        delta = modified_prob - baseline_prob
        
        # Compute reason code deltas
        reason_codes_delta = self._compute_reason_deltas(deltas, delta)
        
        return {
            "probability": float(modified_prob),
            "delta": float(delta),
            "reason_codes_delta": reason_codes_delta
        }
    
    def fast_surrogate(
        self,
        lat: float,
        lon: float,
        date: str,
        deltas: FeatureDelta
    ) -> Dict:
        """
        Fast surrogate model for what-if scenarios.
        
        Uses a lightweight emulator trained on only key features.
        
        TODO: Load actual baseline and use real surrogate
        """
        # Simplified features for surrogate
        baseline_simple = np.array([[
            np.random.rand() * 15 + 5,   # wind_speed_10m
            np.random.rand() * 60 + 20,  # rh
            np.random.rand() * 10,       # rain_24h
            np.random.rand() * 20 + 5,   # gust_10m
        ]])
        
        modified_simple = baseline_simple.copy()
        
        # Apply deltas
        if deltas.wind_speed_10m is not None:
            modified_simple[0, 0] = deltas.wind_speed_10m
        if deltas.rh is not None:
            modified_simple[0, 1] = deltas.rh
        if deltas.rain_24h is not None:
            modified_simple[0, 2] = deltas.rain_24h
        if deltas.gust_10m is not None:
            modified_simple[0, 3] = deltas.gust_10m
        
        # Predict with surrogate
        baseline_prob = self.surrogate(baseline_simple)[0]
        modified_prob = self.surrogate(modified_simple)[0]
        
        delta = modified_prob - baseline_prob
        
        # Compute reason code deltas
        reason_codes_delta = self._compute_reason_deltas(deltas, delta)
        
        return {
            "probability": float(modified_prob),
            "delta": float(delta),
            "reason_codes_delta": reason_codes_delta
        }
    
    def _get_baseline_features(self, lat: float, lon: float, date: str) -> np.ndarray:
        """Get baseline features for location/date"""
        # TODO: Load from actual data source
        features = np.array([[
            np.random.rand() * 15 + 5,   # wind_speed_10m
            np.random.rand() * 60 + 20,  # rh
            np.random.rand() * 10,       # rain_24h
            np.random.rand() * 20 + 5,   # gust_10m
            np.random.rand() * 30 + 280, # t2m
            np.random.rand() * 20 + 270, # dewpoint
            np.random.rand() * 5,        # vpd
            np.sin(np.random.rand() * 2 * np.pi),  # wind_dir_sin
            np.cos(np.random.rand() * 2 * np.pi),  # wind_dir_cos
        ]])
        return features
    
    def _apply_deltas(
        self,
        features: np.ndarray,
        deltas: FeatureDelta
    ) -> np.ndarray:
        """Apply deltas to features"""
        modified = features.copy()
        
        # Map delta fields to feature indices (this is simplified)
        if deltas.wind_speed_10m is not None:
            modified[0, 0] = deltas.wind_speed_10m
        if deltas.rh is not None:
            modified[0, 1] = deltas.rh
        if deltas.rain_24h is not None:
            modified[0, 2] = deltas.rain_24h
        if deltas.gust_10m is not None:
            modified[0, 3] = deltas.gust_10m
        
        return modified
    
    def _compute_reason_deltas(
        self,
        deltas: FeatureDelta,
        total_delta: float
    ) -> List[ReasonCodeDelta]:
        """
        Compute how much each changed feature contributed to delta.
        
        TODO: Use actual SHAP or gradient-based attribution
        """
        reason_codes = []
        
        # Simple proportional attribution (stub)
        n_changed = sum([
            deltas.wind_speed_10m is not None,
            deltas.rh is not None,
            deltas.rain_24h is not None,
            deltas.gust_10m is not None
        ])
        
        if n_changed > 0:
            per_feature = total_delta / n_changed
            
            if deltas.wind_speed_10m is not None:
                reason_codes.append(ReasonCodeDelta(
                    feature="wind_speed_10m",
                    delta_contribution=per_feature
                ))
            if deltas.rh is not None:
                reason_codes.append(ReasonCodeDelta(
                    feature="rh",
                    delta_contribution=per_feature
                ))
            if deltas.rain_24h is not None:
                reason_codes.append(ReasonCodeDelta(
                    feature="rain_24h",
                    delta_contribution=per_feature
                ))
            if deltas.gust_10m is not None:
                reason_codes.append(ReasonCodeDelta(
                    feature="gust_10m",
                    delta_contribution=per_feature
                ))
        
        return reason_codes
