"""
Feature engineering at 0.25 degree spatial resolution
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class FeatureEngineer:
    """
    Engineer features for wildfire risk prediction at 0.25° resolution
    """
    
    def __init__(self, resolution: float = 0.25):
        """
        Initialize feature engineer
        
        Args:
            resolution: Spatial resolution in degrees
        """
        self.resolution = resolution
    
    def aggregate_to_grid(
        self,
        data: pd.DataFrame,
        agg_functions: Dict[str, str] = None
    ) -> pd.DataFrame:
        """
        Aggregate point data to 0.25° grid
        
        Args:
            data: Raw data with latitude/longitude
            agg_functions: Aggregation functions for each column
            
        Returns:
            Gridded data
        """
        # Create grid cells
        data = data.copy()
        data['lat_grid'] = (data['latitude'] / self.resolution).round() * self.resolution
        data['lon_grid'] = (data['longitude'] / self.resolution).round() * self.resolution
        
        # Default aggregations
        if agg_functions is None:
            agg_functions = {
                'temperature': 'mean',
                'humidity': 'mean',
                'wind_speed': 'mean',
                'precipitation': 'sum'
            }
        
        # Group by grid and time
        group_cols = ['lat_grid', 'lon_grid']
        if 'datetime' in data.columns:
            group_cols.append('datetime')
        
        gridded = data.groupby(group_cols).agg(agg_functions).reset_index()
        
        return gridded
    
    def create_temporal_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create temporal features
        
        Args:
            data: Data with datetime column
            
        Returns:
            Data with temporal features
        """
        data = data.copy()
        
        if 'datetime' in data.columns:
            data['hour'] = pd.to_datetime(data['datetime']).dt.hour
            data['day_of_year'] = pd.to_datetime(data['datetime']).dt.dayofyear
            data['month'] = pd.to_datetime(data['datetime']).dt.month
            data['is_summer'] = data['month'].isin([6, 7, 8]).astype(int)
            data['is_fire_season'] = data['month'].isin([5, 6, 7, 8, 9]).astype(int)
        
        return data
    
    def create_weather_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create weather-derived features
        
        Args:
            data: Weather data
            
        Returns:
            Data with derived features
        """
        data = data.copy()
        
        # Derived weather features
        if 'temperature' in data.columns and 'humidity' in data.columns:
            # Vapor pressure deficit
            data['vpd'] = self._calculate_vpd(data['temperature'], data['humidity'])
        
        if 'temperature' in data.columns and 'precipitation' in data.columns:
            # Drought index approximation
            data['drought_index'] = data['temperature'] / (data['precipitation'] + 1)
        
        if 'wind_speed' in data.columns and 'humidity' in data.columns:
            # Fire weather index components
            data['fwi_component'] = data['wind_speed'] * (100 - data['humidity']) / 100
        
        return data
    
    def create_vegetation_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create vegetation-related features
        
        Args:
            data: Data with location
            
        Returns:
            Data with vegetation features
        """
        data = data.copy()
        
        # Placeholder for vegetation indices
        # In production, would derive from satellite data (NDVI, EVI, etc.)
        data['ndvi'] = np.random.uniform(0.2, 0.8, len(data))
        data['evi'] = np.random.uniform(0.1, 0.6, len(data))
        data['fuel_load'] = np.random.uniform(5, 30, len(data))
        
        return data
    
    def create_lag_features(
        self,
        data: pd.DataFrame,
        columns: List[str],
        lags: List[int] = [1, 3, 7]
    ) -> pd.DataFrame:
        """
        Create lagged features
        
        Args:
            data: Time series data
            columns: Columns to lag
            lags: Lag periods (in days)
            
        Returns:
            Data with lag features
        """
        data = data.copy()
        
        for col in columns:
            if col in data.columns:
                for lag in lags:
                    data[f'{col}_lag_{lag}d'] = data.groupby(['lat_grid', 'lon_grid'])[col].shift(lag)
        
        return data
    
    def create_rolling_features(
        self,
        data: pd.DataFrame,
        columns: List[str],
        windows: List[int] = [7, 14, 30]
    ) -> pd.DataFrame:
        """
        Create rolling window features
        
        Args:
            data: Time series data
            columns: Columns for rolling features
            windows: Window sizes (in days)
            
        Returns:
            Data with rolling features
        """
        data = data.copy()
        
        for col in columns:
            if col in data.columns:
                for window in windows:
                    data[f'{col}_rolling_mean_{window}d'] = data.groupby(['lat_grid', 'lon_grid'])[col].transform(
                        lambda x: x.rolling(window, min_periods=1).mean()
                    )
        
        return data
    
    def _calculate_vpd(self, temperature: pd.Series, humidity: pd.Series) -> pd.Series:
        """
        Calculate Vapor Pressure Deficit
        
        Args:
            temperature: Temperature in Celsius
            humidity: Relative humidity (0-100)
            
        Returns:
            VPD in kPa
        """
        # Saturation vapor pressure (kPa)
        es = 0.611 * np.exp((17.27 * temperature) / (temperature + 237.3))
        
        # Actual vapor pressure
        ea = es * (humidity / 100)
        
        # VPD
        vpd = es - ea
        
        return vpd
    
    def engineer_all_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps
        
        Args:
            data: Raw data
            
        Returns:
            Fully engineered features
        """
        # Grid aggregation
        data = self.aggregate_to_grid(data)
        
        # Temporal features
        data = self.create_temporal_features(data)
        
        # Weather features
        data = self.create_weather_features(data)
        
        # Vegetation features
        data = self.create_vegetation_features(data)
        
        # Lag features
        weather_cols = ['temperature', 'humidity', 'precipitation']
        data = self.create_lag_features(data, weather_cols)
        
        # Rolling features
        data = self.create_rolling_features(data, weather_cols)
        
        return data
