"""
Explainability service - SHAP, PDP, ICE helpers
"""
from typing import List
import numpy as np

from app.models.schemas import FeatureContribution, FeatureInteraction
from app.models.registry import ModelRegistry


class ExplainService:
    """Service for model explainability"""
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.bundle = registry.get_bundle()
    
    def compute_local_shap(
        self,
        lat: float,
        lon: float,
        date: str
    ) -> List[FeatureContribution]:
        """
        Compute local SHAP values for a specific location.
        
        TODO: Replace with actual SHAP computation using shap library
        """
        # Fabricated SHAP values for demonstration
        contributions = [
            FeatureContribution(
                feature="wind_speed_10m",
                value=12.5,
                unit="m/s",
                contribution=0.08
            ),
            FeatureContribution(
                feature="rh",
                value=35.0,
                unit="%",
                contribution=-0.12
            ),
            FeatureContribution(
                feature="rain_24h",
                value=0.0,
                unit="mm",
                contribution=-0.05
            ),
            FeatureContribution(
                feature="gust_10m",
                value=18.0,
                unit="m/s",
                contribution=0.04
            ),
            FeatureContribution(
                feature="t2m",
                value=305.0,
                unit="K",
                contribution=0.06
            ),
            FeatureContribution(
                feature="vpd",
                value=2.5,
                unit="kPa",
                contribution=0.07
            ),
        ]
        
        return contributions
    
    def compute_interactions(
        self,
        lat: float,
        lon: float,
        date: str
    ) -> List[FeatureInteraction]:
        """
        Compute feature interactions (e.g., RH × Wind).
        
        TODO: Replace with actual interaction computation
        """
        interactions = [
            FeatureInteraction(
                pair=("rh", "wind_speed_10m"),
                value=0.15
            ),
            FeatureInteraction(
                pair=("t2m", "rh"),
                value=-0.08
            ),
        ]
        return interactions
    
    def check_ood(self, lat: float, lon: float, date: str) -> bool:
        """
        Check if features are out-of-distribution.
        
        TODO: Use actual feature ranges from training
        """
        # Stub: randomly flag 5% as OOD
        return np.random.rand() < 0.05
    
    def pdp_sample(self, feature: str, n_points: int = 50) -> dict:
        """
        Compute partial dependence plot data for a feature.
        
        TODO: Implement actual PDP computation
        """
        # Stub
        values = np.linspace(0, 1, n_points)
        effects = np.sin(values * np.pi) * 0.3
        
        return {
            "feature": feature,
            "values": values.tolist(),
            "effects": effects.tolist()
        }
    
    def interaction_tile(
        self,
        feature1: str,
        feature2: str,
        resolution: int = 20
    ) -> dict:
        """
        Compute 2D interaction heatmap.
        
        TODO: Implement actual interaction computation
        """
        # Stub: return a simple grid
        x = np.linspace(0, 1, resolution)
        y = np.linspace(0, 1, resolution)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X * np.pi) * np.cos(Y * np.pi)
        
        return {
            "feature1": feature1,
            "feature2": feature2,
            "x": x.tolist(),
            "y": y.tolist(),
            "z": Z.tolist()
        }
