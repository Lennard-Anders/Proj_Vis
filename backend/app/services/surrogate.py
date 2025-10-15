"""
Surrogate model service for fast inference
"""
import numpy as np
from typing import Any, List


class SurrogateModel:
    """
    Fast surrogate model for real-time spread prediction
    Uses simplified physics-based approximation
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = [
            "temperature",
            "humidity",
            "wind_speed",
            "wind_direction",
            "fuel_type",
            "slope"
        ]
    
    def load(self, path: str):
        """Load surrogate model from disk"""
        # Placeholder for loading surrogate model
        pass
    
    def predict_spread(
        self, 
        ignition_point: tuple,
        weather_conditions: dict,
        fuel_conditions: dict,
        time_hours: int
    ) -> dict:
        """
        Predict fire spread from ignition point
        
        Args:
            ignition_point: (lat, lon) tuple
            weather_conditions: Weather parameters
            fuel_conditions: Fuel parameters
            time_hours: Simulation duration
            
        Returns:
            Dictionary with spread prediction
        """
        # Simplified Rothermel model approximation
        wind_speed = weather_conditions.get("wind_speed", 5.0)
        humidity = weather_conditions.get("humidity", 30.0)
        temperature = weather_conditions.get("temperature", 25.0)
        
        # Rate of spread (m/min) - simplified
        ros_base = 0.5
        wind_factor = 1.0 + (wind_speed / 10.0)
        humidity_factor = max(0.5, 1.5 - (humidity / 100.0))
        temp_factor = 1.0 + (temperature - 20.0) / 30.0
        
        rate_of_spread = ros_base * wind_factor * humidity_factor * temp_factor
        
        # Distance in km
        max_distance = rate_of_spread * 60 * time_hours / 1000
        
        return {
            "rate_of_spread_m_per_min": rate_of_spread,
            "max_distance_km": max_distance,
            "spread_direction": weather_conditions.get("wind_direction", 0),
            "confidence": 0.7
        }
    
    def predict_batch(self, inputs: List[dict]) -> List[dict]:
        """
        Batch prediction for multiple scenarios
        
        Args:
            inputs: List of input dictionaries
            
        Returns:
            List of prediction dictionaries
        """
        return [self.predict_spread(**inp) for inp in inputs]


# Global surrogate model instance
_surrogate = SurrogateModel()


def get_surrogate() -> SurrogateModel:
    """Get the surrogate model instance"""
    return _surrogate


def load_surrogate(path: str):
    """Load surrogate model from path"""
    _surrogate.load(path)
