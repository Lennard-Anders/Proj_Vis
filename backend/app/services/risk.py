"""
Risk assessment service - model inference and calibration
"""
import numpy as np
from typing import List

from app.models.schemas import RiskTile, BBox
from app.models.registry import ModelRegistry


class RiskService:
    """Service for risk assessment"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.bundle = registry.get_bundle()
    
    def compute_risk_grid(self, date: str, bbox: BBox) -> List[RiskTile]:
        """
        Compute risk for a grid of 0.25° tiles within bbox.
        
        TODO: Load actual features from DuckDB/Parquet
        TODO: Apply model inference with calibration per region
        """
        tiles = []
        
        # Generate 0.25° grid
        resolution = 0.25
        lats = np.arange(bbox.min_lat, bbox.max_lat, resolution)
        lons = np.arange(bbox.min_lon, bbox.max_lon, resolution)
        
        for lat in lats:
            for lon in lons:
                # TODO: Fetch actual features for this lat/lon/date
                # For now, generate synthetic features
                features = self._generate_synthetic_features(lat, lon, date)
                
                # Predict with model
                prob, ci_lower, ci_upper = self._predict_single(features)
                
                tiles.append(RiskTile(
                    lat=float(lat),
                    lon=float(lon),
                    prob=float(prob),
                    ci=(float(ci_lower), float(ci_upper))
                ))
        
        return tiles
    
    def _generate_synthetic_features(self, lat: float, lon: float, date: str) -> np.ndarray:
        """Generate synthetic features for testing"""
        # Create a single row of features
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
    
    def _predict_single(self, features: np.ndarray) -> tuple:
        """Predict for a single location with CI"""
        prob, ci_lower, ci_upper = self.bundle.predict_with_ci(features)
        return prob[0], ci_lower[0], ci_upper[0]
