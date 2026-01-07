"""Temperature data service for historical temperature analysis."""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Paths to temperature datasets
DATA_DIR = Path("/app/data/Datasets")
AMERICA_DATA = DATA_DIR / "df_america_cleaned.csv"
CITY_DATA = DATA_DIR / "GlobalLandTemperaturesByCity.csv"
COUNTRY_DATA = DATA_DIR / "GlobalLandTemperaturesByCountry.csv"

# Path to current temperature CSV (pre-fetched data)
TEMPERATURE_CURRENT_CSV = Path("/app/data") / "temperature_current.csv"

class TemperatureService:
    """Service for loading and processing temperature data."""
    
    def __init__(self):
        self._america_df: Optional[pd.DataFrame] = None
        self._city_df: Optional[pd.DataFrame] = None
        self._country_df: Optional[pd.DataFrame] = None
        self._current_temp_df: Optional[pd.DataFrame] = None
        self._date_range_cache: Optional[Dict[str, Any]] = None
        self._load_current_temperature_csv()
    
    def _load_current_temperature_csv(self):
        """Load current temperature data from CSV."""
        try:
            if TEMPERATURE_CURRENT_CSV.exists():
                self._current_temp_df = pd.read_csv(TEMPERATURE_CURRENT_CSV)
                logger.info(f"Loaded {len(self._current_temp_df)} temperature points from CSV")
            else:
                logger.warning(f"Temperature CSV not found at {TEMPERATURE_CURRENT_CSV}")
        except Exception as e:
            logger.error(f"Error loading temperature CSV: {e}")
    
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
        Uses pre-fetched CSV data instead of historical datasets.
        
        Args:
            date_str: Date (ignored, uses current CSV data)
            region: Optional region filter
            bbox: Optional bounding box {min_lat, max_lat, min_lon, max_lon}
        
        Returns:
            List of temperature points with lat, lon, temperature
        """
        try:
            # Use current temperature CSV if available
            if self._current_temp_df is not None and len(self._current_temp_df) > 0:
                df = self._current_temp_df.copy()
                
                # Apply bounding box filter if provided
                if bbox:
                    df = df[
                        (df['latitude'] >= bbox['min_lat']) &
                        (df['latitude'] <= bbox['max_lat']) &
                        (df['longitude'] >= bbox['min_lon']) &
                        (df['longitude'] <= bbox['max_lon'])
                    ]
                
                # Convert to heatmap format
                heatmap_data = []
                for _, row in df.iterrows():
                    heatmap_data.append({
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'temperature': float(row['temperature']),
                        'uncertainty': 0.0,
                        'city': '',
                        'country': ''
                    })
                
                logger.info(f"Returning {len(heatmap_data)} temperature points from CSV")
                return heatmap_data
            
            # Fallback to historical data if CSV not available
            logger.warning("Temperature CSV not available, using historical data")
            return self._get_temperature_from_historical(date_str, region, bbox)
        
        except Exception as e:
            logger.error(f"Error getting temperature heatmap: {e}")
            return []
    
    def _get_temperature_from_historical(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Fallback method using historical datasets."""
        try:
            target_date = pd.to_datetime(date_str)
            
            # Load data based on region
            if region and region.lower() in ['california', 'north_america', 'south_america', 'americas']:
                df = self._load_america_data()
            else:
                df = self._load_city_data()

            if df is None or df.empty:
                logger.warning("No temperature data available after loading datasets")
                return []
            
            # Get latest available date and use it if requested date is too recent
            latest_date = df['dt'].max()
            if target_date > latest_date:
                logger.info(f"Requested date {date_str} is beyond data range, using latest: {latest_date.strftime('%Y-%m-%d')}")
                target_date = latest_date
            
            target_month = f"{target_date.year}-{target_date.month:02d}"
            
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
    
    def get_date_range(self, region: Optional[str] = None) -> Dict[str, Any]:
        """Get available date range in the dataset."""
        try:
            if region and region.lower() in ['california', 'north_america', 'south_america', 'americas']:
                df = self._load_america_data()
            else:
                df = self._load_city_data()
            
            if df is None or df.empty:
                return {'min_date': None, 'max_date': None}
            
            return {
                'min_date': df['dt'].min().strftime('%Y-%m-%d'),
                'max_date': df['dt'].max().strftime('%Y-%m-%d')
            }
        except Exception as e:
            logger.error(f"Error getting date range: {e}")
            return {'min_date': None, 'max_date': None}


# Global instance
temperature_service = TemperatureService()
