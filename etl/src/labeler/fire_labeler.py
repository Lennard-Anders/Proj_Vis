"""
Labeler for creating training labels from historical fire data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class FireLabeler:
    """
    Creates labels for wildfire risk prediction from historical fire occurrences
    """
    
    def __init__(self, fire_perimeter_data: Optional[pd.DataFrame] = None):
        """
        Initialize labeler
        
        Args:
            fire_perimeter_data: Historical fire perimeter data
        """
        self.fire_data = fire_perimeter_data
    
    def load_fire_history(self, filepath: str) -> pd.DataFrame:
        """
        Load historical fire data
        
        Args:
            filepath: Path to fire history data
            
        Returns:
            DataFrame with fire history
        """
        # Placeholder for loading actual fire data
        # In production, would load from NIFC, MTBS, or other sources
        
        self.fire_data = pd.DataFrame({
            'fire_id': range(100),
            'start_date': pd.date_range('2020-01-01', periods=100, freq='3D'),
            'latitude': np.random.uniform(30, 45, 100),
            'longitude': np.random.uniform(-125, -100, 100),
            'area_hectares': np.random.exponential(1000, 100),
            'cause': np.random.choice(['lightning', 'human', 'unknown'], 100)
        })
        
        return self.fire_data
    
    def create_labels(
        self,
        weather_data: pd.DataFrame,
        time_window_days: int = 7,
        distance_threshold_km: float = 10.0
    ) -> pd.DataFrame:
        """
        Create binary labels for fire occurrence
        
        Args:
            weather_data: Weather observations with lat/lon/datetime
            time_window_days: Time window for considering fire occurrence
            distance_threshold_km: Spatial distance threshold
            
        Returns:
            DataFrame with labels
        """
        if self.fire_data is None:
            raise ValueError("Fire history data not loaded")
        
        # Placeholder labeling logic
        # In production, would perform spatiotemporal join
        
        weather_data = weather_data.copy()
        weather_data['fire_occurred'] = np.random.binomial(1, 0.1, len(weather_data))
        weather_data['fire_size_class'] = np.random.choice(['A', 'B', 'C', 'D', 'E'], len(weather_data))
        weather_data['days_until_fire'] = np.random.randint(0, time_window_days, len(weather_data))
        
        return weather_data
    
    def create_continuous_labels(
        self,
        weather_data: pd.DataFrame,
        radius_km: float = 25.0
    ) -> pd.DataFrame:
        """
        Create continuous risk labels (e.g., fire intensity)
        
        Args:
            weather_data: Weather observations
            radius_km: Radius for aggregating fire activity
            
        Returns:
            DataFrame with continuous labels
        """
        weather_data = weather_data.copy()
        
        # Placeholder for continuous labeling
        weather_data['fire_intensity'] = np.random.gamma(2, 2, len(weather_data))
        weather_data['burned_area_nearby'] = np.random.exponential(100, len(weather_data))
        
        return weather_data
    
    def balance_dataset(
        self,
        labeled_data: pd.DataFrame,
        target_col: str = 'fire_occurred',
        method: str = 'undersample'
    ) -> pd.DataFrame:
        """
        Balance dataset for training
        
        Args:
            labeled_data: Labeled dataset
            target_col: Target column name
            method: Balancing method ('undersample', 'oversample', or 'smote')
            
        Returns:
            Balanced dataset
        """
        if target_col not in labeled_data.columns:
            return labeled_data
        
        # Simple undersampling for demo
        if method == 'undersample':
            positive = labeled_data[labeled_data[target_col] == 1]
            negative = labeled_data[labeled_data[target_col] == 0]
            
            if len(negative) > len(positive):
                negative = negative.sample(len(positive), random_state=42)
            
            balanced = pd.concat([positive, negative]).sample(frac=1, random_state=42)
            return balanced
        
        return labeled_data
    
    def get_label_statistics(self, labeled_data: pd.DataFrame) -> Dict:
        """
        Get statistics about labels
        
        Args:
            labeled_data: Labeled dataset
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_samples': len(labeled_data),
            'positive_samples': labeled_data['fire_occurred'].sum() if 'fire_occurred' in labeled_data else 0,
            'negative_samples': len(labeled_data) - (labeled_data['fire_occurred'].sum() if 'fire_occurred' in labeled_data else 0),
            'positive_rate': labeled_data['fire_occurred'].mean() if 'fire_occurred' in labeled_data else 0
        }
        
        return stats
