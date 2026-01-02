"""Temperature data service for historical temperature analysis."""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Paths to temperature datasets (mounts put files directly under /app/data)
DATA_DIR = Path("/app/data")
AMERICA_DATA = DATA_DIR / "df_america_cleaned.csv"
CITY_DATA = DATA_DIR / "GlobalLandTemperaturesByCity.csv"
COUNTRY_DATA = DATA_DIR / "GlobalLandTemperaturesByCountry.csv"

class TemperatureService:
    """Service for loading and processing temperature data."""
    
    def __init__(self):
        self._america_df: Optional[pd.DataFrame] = None
        self._city_df: Optional[pd.DataFrame] = None
        self._country_df: Optional[pd.DataFrame] = None
    
    def _load_america_data(self) -> pd.DataFrame:
        """Load America temperature data."""
        if self._america_df is None:
            if not AMERICA_DATA.exists():
                logger.warning("America temperature dataset missing at %s, falling back to city data", AMERICA_DATA)
                return self._load_city_data()
            logger.info("Loading America temperature data...")
            self._america_df = pd.read_csv(AMERICA_DATA)
            self._america_df['dt'] = pd.to_datetime(self._america_df['dt'])
            self._america_df['lat'] = self._america_df['Latitude'].apply(self._parse_coordinate)
            self._america_df['lon'] = self._america_df['Longitude'].apply(self._parse_coordinate)
        return self._america_df
    
    def _load_city_data(self) -> pd.DataFrame:
        """Load global city temperature data."""
        if self._city_df is None:
            if not CITY_DATA.exists():
                logger.error("City temperature dataset missing at %s", CITY_DATA)
                self._city_df = pd.DataFrame()
                return self._city_df
            logger.info("Loading global city temperature data...")
            self._city_df = pd.read_csv(CITY_DATA)
            self._city_df['dt'] = pd.to_datetime(self._city_df['dt'])
            self._city_df['lat'] = self._city_df['Latitude'].apply(self._parse_coordinate)
            self._city_df['lon'] = self._city_df['Longitude'].apply(self._parse_coordinate)
        return self._city_df
    
    @staticmethod
    def _parse_coordinate(coord_str: str) -> float:
        """Parse coordinate string like '49.03N' or '122.45W' to float."""
        if pd.isna(coord_str):
            return 0.0
        coord_str = str(coord_str).strip()
        direction = coord_str[-1]
        value = float(coord_str[:-1])
        if direction in ['S', 'W']:
            value = -value
        return value
    
    def get_temperature_heatmap(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get temperature data for heatmap visualization.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            region: Optional region filter (e.g., 'california', 'north_america')
            bbox: Optional bounding box {min_lat, max_lat, min_lon, max_lon}
        
        Returns:
            List of temperature points with lat, lon, temperature
        """
        try:
            target_date = pd.to_datetime(date_str)
            target_month = f"{target_date.year}-{target_date.month:02d}"
            
            # Load data based on region
            if region and region.lower() in ['california', 'north_america', 'south_america', 'americas']:
                df = self._load_america_data()
            else:
                df = self._load_city_data()

            if df is None or df.empty:
                logger.warning("No temperature data available after loading datasets")
                return []
            
            # Filter by date (month-year match)
            df['year_month'] = df['dt'].dt.to_period('M').astype(str)
            filtered = df[df['year_month'] == target_month].copy()
            
            # Apply bounding box filter if provided
            if bbox:
                filtered = filtered[
                    (filtered['lat'] >= bbox['min_lat']) &
                    (filtered['lat'] <= bbox['max_lat']) &
                    (filtered['lon'] >= bbox['min_lon']) &
                    (filtered['lon'] <= bbox['max_lon'])
                ]
            
            # Remove rows with missing temperature data
            filtered = filtered.dropna(subset=['AverageTemperature', 'lat', 'lon'])
            
            # Convert to heatmap format
            heatmap_data = []
            for _, row in filtered.iterrows():
                heatmap_data.append({
                    'latitude': float(row['lat']),
                    'longitude': float(row['lon']),
                    'temperature': float(row['AverageTemperature']),
                    'uncertainty': float(row.get('AverageTemperatureUncertainty', 0)),
                    'city': row.get('City', ''),
                    'country': row.get('Country', '')
                })
            
            logger.info(f"Found {len(heatmap_data)} temperature points for {date_str}")
            return heatmap_data
        
        except Exception as e:
            logger.error(f"Error getting temperature heatmap: {e}")
            return []
    
    def get_historical_stats(
        self,
        lat: float,
        lon: float,
        radius_km: float = 50
    ) -> Dict[str, Any]:
        """
        Get historical temperature statistics for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers
        
        Returns:
            Statistical summary of historical temperatures
        """
        try:
            df = self._load_city_data()
            
            # Simple distance filter (approximate)
            lat_range = radius_km / 111.0  # 1 degree lat ~ 111 km
            lon_range = radius_km / (111.0 * abs(pd.np.cos(pd.np.radians(lat))))
            
            nearby = df[
                (df['lat'].between(lat - lat_range, lat + lat_range)) &
                (df['lon'].between(lon - lon_range, lon + lon_range))
            ].copy()
            
            nearby = nearby.dropna(subset=['AverageTemperature'])
            
            if len(nearby) == 0:
                return {
                    'mean_temp': 20.0,
                    'max_temp': 35.0,
                    'min_temp': 5.0,
                    'std_temp': 10.0,
                    'data_points': 0
                }
            
            stats = {
                'mean_temp': float(nearby['AverageTemperature'].mean()),
                'max_temp': float(nearby['AverageTemperature'].max()),
                'min_temp': float(nearby['AverageTemperature'].min()),
                'std_temp': float(nearby['AverageTemperature'].std()),
                'data_points': len(nearby)
            }
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting historical stats: {e}")
            return {
                'mean_temp': 20.0,
                'max_temp': 35.0,
                'min_temp': 5.0,
                'std_temp': 10.0,
                'data_points': 0
            }


# Global instance
temperature_service = TemperatureService()
