"""Weather data service using pre-fetched CSV files from Google Earth Engine."""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Paths to cached weather CSV files
DATA_DIR = Path("/app/data")
WIND_CSV = DATA_DIR / "wind_current.csv"
HUMIDITY_CSV = DATA_DIR / "humidity_current.csv"
RAIN_CSV = DATA_DIR / "rain_current.csv"
TEMPERATURE_CSV = DATA_DIR / "temperature_current.csv"
METADATA_CSV = DATA_DIR / "weather_metadata.csv"


class WeatherService:
    """Service for loading pre-fetched weather data from CSV files."""
    
    def __init__(self):
        self._wind_df: Optional[pd.DataFrame] = None
        self._humidity_df: Optional[pd.DataFrame] = None
        self._rain_df: Optional[pd.DataFrame] = None
        self._temperature_df: Optional[pd.DataFrame] = None
        self._metadata: Optional[Dict] = None
        self._load_csv_data()
    
    def _load_csv_data(self):
        """Load weather data from CSV files."""
        try:
            if WIND_CSV.exists():
                self._wind_df = pd.read_csv(WIND_CSV)
                logger.info(f"Loaded {len(self._wind_df)} wind points from CSV")
            else:
                logger.warning(f"Wind CSV not found at {WIND_CSV}")
            
            if HUMIDITY_CSV.exists():
                self._humidity_df = pd.read_csv(HUMIDITY_CSV)
                logger.info(f"Loaded {len(self._humidity_df)} humidity points from CSV")
            else:
                logger.warning(f"Humidity CSV not found at {HUMIDITY_CSV}")
            
            if RAIN_CSV.exists():
                self._rain_df = pd.read_csv(RAIN_CSV)
                logger.info(f"Loaded {len(self._rain_df)} rain points from CSV")
            else:
                logger.warning(f"Rain CSV not found at {RAIN_CSV}")
            
            if TEMPERATURE_CSV.exists():
                self._temperature_df = pd.read_csv(TEMPERATURE_CSV)
                logger.info(f"Loaded {len(self._temperature_df)} temperature points from CSV")
            else:
                logger.warning(f"Temperature CSV not found at {TEMPERATURE_CSV}")
            
            if METADATA_CSV.exists():
                metadata_df = pd.read_csv(METADATA_CSV)
                self._metadata = metadata_df.iloc[0].to_dict() if len(metadata_df) > 0 else {}
                logger.info(f"Weather data date: {self._metadata.get('data_date', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error loading weather CSV files: {e}")
    
    
    def get_wind_heatmap(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get wind speed data from pre-fetched CSV.
        
        Args:
            date_str: Date (ignored, always returns latest cached data)
            region: Region filter (ignored)
            bbox: Bounding box filter (optional)
        
        Returns:
            List of wind data points with lat, lon, wind_speed
        """
        if self._wind_df is None or len(self._wind_df) == 0:
            logger.warning("No wind data available in CSV")
            return []
        
        df = self._wind_df.copy()
        
        # Apply bounding box filter if provided
        if bbox:
            df = df[
                (df['latitude'] >= bbox['min_lat']) &
                (df['latitude'] <= bbox['max_lat']) &
                (df['longitude'] >= bbox['min_lon']) &
                (df['longitude'] <= bbox['max_lon'])
            ]
        
        # Convert to list of dicts
        result = df.to_dict('records')
        logger.info(f"Returning {len(result)} wind points from CSV")
        return result
    
    def get_humidity_heatmap(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Get humidity data from pre-fetched CSV."""
        if self._humidity_df is None or len(self._humidity_df) == 0:
            logger.warning("No humidity data available in CSV")
            return []
        
        df = self._humidity_df.copy()
        
        if bbox:
            df = df[
                (df['latitude'] >= bbox['min_lat']) &
                (df['latitude'] <= bbox['max_lat']) &
                (df['longitude'] >= bbox['min_lon']) &
                (df['longitude'] <= bbox['max_lon'])
            ]
        
        result = df.to_dict('records')
        logger.info(f"Returning {len(result)} humidity points from CSV")
        return result
    
    def get_rain_heatmap(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Get precipitation data from pre-fetched CSV."""
        if self._rain_df is None or len(self._rain_df) == 0:
            logger.warning("No rain data available in CSV")
            return []
        
        df = self._rain_df.copy()
        
        if bbox:
            df = df[
                (df['latitude'] >= bbox['min_lat']) &
                (df['latitude'] <= bbox['max_lat']) &
                (df['longitude'] >= bbox['min_lon']) &
                (df['longitude'] <= bbox['max_lon'])
            ]
        
        result = df.to_dict('records')
        logger.info(f"Returning {len(result)} rain points from CSV")
        return result
    
    def get_temperature_heatmap(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Get temperature data from pre-fetched CSV."""
        if self._temperature_df is None or len(self._temperature_df) == 0:
            logger.warning("No temperature data available in CSV")
            return []
        
        df = self._temperature_df.copy()
        
        if bbox:
            df = df[
                (df['latitude'] >= bbox['min_lat']) &
                (df['latitude'] <= bbox['max_lat']) &
                (df['longitude'] >= bbox['min_lon']) &
                (df['longitude'] <= bbox['max_lon'])
            ]
        
        result = df.to_dict('records')
        logger.info(f"Returning {len(result)} temperature points from CSV")
        return result



# Global instance
weather_service = WeatherService()

