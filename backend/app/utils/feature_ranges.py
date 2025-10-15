"""
Feature ranges and out-of-distribution checks
"""
import json
from pathlib import Path
from typing import Dict, List, Any
import numpy as np


class FeatureRanges:
    """Manage feature ranges from training data"""
    
    def __init__(self, ranges_path: str = None):
        self.ranges = {}
        if ranges_path and Path(ranges_path).exists():
            self.load(ranges_path)
        else:
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default ranges for development"""
        self.ranges = {
            "wind_speed_10m": {"min": 0.0, "max": 30.0, "unit": "m/s"},
            "rh": {"min": 0.0, "max": 100.0, "unit": "%"},
            "rain_24h": {"min": 0.0, "max": 100.0, "unit": "mm"},
            "gust_10m": {"min": 0.0, "max": 50.0, "unit": "m/s"},
            "t2m": {"min": 250.0, "max": 320.0, "unit": "K"},
            "dewpoint": {"min": 240.0, "max": 310.0, "unit": "K"},
            "vpd": {"min": 0.0, "max": 8.0, "unit": "kPa"},
            "rain_72h": {"min": 0.0, "max": 200.0, "unit": "mm"},
            "recent_fires_72h_20km": {"min": 0, "max": 100, "unit": "count"}
        }
    
    def load(self, path: str):
        """Load ranges from JSON file"""
        with open(path, 'r') as f:
            self.ranges = json.load(f)
    
    def save(self, path: str):
        """Save ranges to JSON file"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.ranges, f, indent=2)
    
    def check_ood(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Check if features are out-of-distribution.
        
        Args:
            features: Dictionary mapping feature names to values
        
        Returns:
            Dictionary with OOD status and flagged features
        """
        flags = []
        
        for feature, value in features.items():
            if feature not in self.ranges:
                continue
            
            range_info = self.ranges[feature]
            min_val = range_info["min"]
            max_val = range_info["max"]
            
            if value < min_val:
                flags.append({
                    "feature": feature,
                    "value": value,
                    "bound": "below_min",
                    "threshold": min_val
                })
            elif value > max_val:
                flags.append({
                    "feature": feature,
                    "value": value,
                    "bound": "above_max",
                    "threshold": max_val
                })
        
        return {
            "ood": len(flags) > 0,
            "flags": flags
        }
    
    def get_range(self, feature: str) -> Dict[str, Any]:
        """Get range info for a specific feature"""
        return self.ranges.get(feature, {})
