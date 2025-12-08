"""Weather data service using Google Earth Engine for wind, humidity, and rain data."""
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np

# Add etl directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'etl'))

try:
    import ee
    from gee_connector import GEEDataPipeline
    GEE_AVAILABLE = True
except Exception as e:
    GEE_AVAILABLE = False
    logging.warning(f"GEE not available: {e}")

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather heatmap data from Google Earth Engine."""
    
    def __init__(self):
        self._gee_pipeline: Optional[GEEDataPipeline] = None
        if GEE_AVAILABLE:
            try:
                self._gee_pipeline = GEEDataPipeline()
                logger.info("GEE Weather Service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize GEE: {e}")
    
    def _generate_grid_points(
        self,
        bbox: Optional[Dict[str, float]] = None,
        grid_resolution: float = 1.0
    ) -> List[Dict[str, float]]:
        """Generate a grid of points for sampling weather data."""
        if bbox:
            min_lat = bbox['min_lat']
            max_lat = bbox['max_lat']
            min_lon = bbox['min_lon']
            max_lon = bbox['max_lon']
        else:
            # Default to global coverage (sparse)
            min_lat, max_lat = -60, 75  # Exclude poles
            min_lon, max_lon = -180, 180
        
        lats = np.arange(min_lat, max_lat, grid_resolution)
        lons = np.arange(min_lon, max_lon, grid_resolution)
        
        points = []
        for lat in lats:
            for lon in lons:
                points.append({'latitude': float(lat), 'longitude': float(lon)})
        
        return points
    
    def get_wind_heatmap(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get wind speed data for heatmap visualization using GEE.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            region: Optional region filter
            bbox: Optional bounding box {min_lat, max_lat, min_lon, max_lon}
        
        Returns:
            List of wind data points with lat, lon, wind_speed
        """
        if not GEE_AVAILABLE or not self._gee_pipeline:
            logger.warning("GEE not available, returning mock data")
            return self._generate_mock_wind_data(bbox)
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            start_date = (target_date - timedelta(days=3)).strftime('%Y-%m-%d')
            end_date = (target_date + timedelta(days=3)).strftime('%Y-%m-%d')
            
            # Generate grid points
            grid_points = self._generate_grid_points(bbox, grid_resolution=2.0)
            
            heatmap_data = []
            for point in grid_points[:500]:  # Limit to 500 points for performance
                try:
                    ee_point = ee.Geometry.Point([point['longitude'], point['latitude']])
                    region_buffer = ee_point.buffer(25000)  # 25km buffer
                    
                    weather = self._gee_pipeline.get_weather_data(region_buffer, start_date, end_date)
                    
                    if weather and weather.get('wind_speed') is not None:
                        heatmap_data.append({
                            'latitude': point['latitude'],
                            'longitude': point['longitude'],
                            'wind_speed': float(weather['wind_speed'])
                        })
                except Exception as e:
                    logger.debug(f"Failed to fetch wind for point {point}: {e}")
                    continue
            
            logger.info(f"Fetched {len(heatmap_data)} wind data points from GEE")
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Error getting wind heatmap from GEE: {e}")
            return self._generate_mock_wind_data(bbox)
    
    def get_humidity_heatmap(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Get humidity data for heatmap visualization using GEE."""
        if not GEE_AVAILABLE or not self._gee_pipeline:
            logger.warning("GEE not available, returning mock data")
            return self._generate_mock_humidity_data(bbox)
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            start_date = (target_date - timedelta(days=3)).strftime('%Y-%m-%d')
            end_date = (target_date + timedelta(days=3)).strftime('%Y-%m-%d')
            
            grid_points = self._generate_grid_points(bbox, grid_resolution=2.0)
            
            heatmap_data = []
            for point in grid_points[:500]:
                try:
                    ee_point = ee.Geometry.Point([point['longitude'], point['latitude']])
                    region_buffer = ee_point.buffer(25000)
                    
                    weather = self._gee_pipeline.get_weather_data(region_buffer, start_date, end_date)
                    
                    if weather and weather.get('humidity_min') is not None:
                        heatmap_data.append({
                            'latitude': point['latitude'],
                            'longitude': point['longitude'],
                            'humidity': float(weather['humidity_min'])
                        })
                except Exception as e:
                    logger.debug(f"Failed to fetch humidity for point {point}: {e}")
                    continue
            
            logger.info(f"Fetched {len(heatmap_data)} humidity data points from GEE")
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Error getting humidity heatmap from GEE: {e}")
            return self._generate_mock_humidity_data(bbox)
    
    def get_rain_heatmap(
        self,
        date_str: str,
        region: Optional[str] = None,
        bbox: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Get precipitation data for heatmap visualization using GEE."""
        if not GEE_AVAILABLE or not self._gee_pipeline:
            logger.warning("GEE not available, returning mock data")
            return self._generate_mock_rain_data(bbox)
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            start_date = (target_date - timedelta(days=3)).strftime('%Y-%m-%d')
            end_date = (target_date + timedelta(days=3)).strftime('%Y-%m-%d')
            
            grid_points = self._generate_grid_points(bbox, grid_resolution=2.0)
            
            heatmap_data = []
            for point in grid_points[:500]:
                try:
                    ee_point = ee.Geometry.Point([point['longitude'], point['latitude']])
                    region_buffer = ee_point.buffer(25000)
                    
                    weather = self._gee_pipeline.get_weather_data(region_buffer, start_date, end_date)
                    
                    if weather and weather.get('precipitation') is not None:
                        heatmap_data.append({
                            'latitude': point['latitude'],
                            'longitude': point['longitude'],
                            'rain': float(weather['precipitation'])
                        })
                except Exception as e:
                    logger.debug(f"Failed to fetch rain for point {point}: {e}")
                    continue
            
            logger.info(f"Fetched {len(heatmap_data)} precipitation data points from GEE")
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Error getting rain heatmap from GEE: {e}")
            return self._generate_mock_rain_data(bbox)
    
    def _generate_mock_wind_data(self, bbox: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Generate mock wind data for fallback."""
        grid_points = self._generate_grid_points(bbox, grid_resolution=3.0)
        return [
            {
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'wind_speed': float(5 + np.random.rand() * 15)  # 5-20 m/s
            }
            for point in grid_points[:200]
        ]
    
    def _generate_mock_humidity_data(self, bbox: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Generate mock humidity data for fallback."""
        grid_points = self._generate_grid_points(bbox, grid_resolution=3.0)
        return [
            {
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'humidity': float(40 + np.random.rand() * 50)  # 40-90%
            }
            for point in grid_points[:200]
        ]
    
    def _generate_mock_rain_data(self, bbox: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Generate mock rain data for fallback."""
        grid_points = self._generate_grid_points(bbox, grid_resolution=3.0)
        return [
            {
                'latitude': point['latitude'],
                'longitude': point['longitude'],
                'rain': float(np.random.rand() * 30)  # 0-30 mm
            }
            for point in grid_points[:200]
        ]


# Global instance
weather_service = WeatherService()
