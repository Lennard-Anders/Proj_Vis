"""
Google Earth Engine Data Pipeline
Fetches satellite imagery and environmental data for wildfire risk analysis
"""
import ee
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GEEDataPipeline:
    """Google Earth Engine data pipeline for wildfire risk features"""
    
    def __init__(self, service_account_key: Optional[str] = None, project: Optional[str] = None):
        """Initialize GEE connection, preferring a service account key from env."""
        # Resolve config from env if not explicitly provided
        key_path = service_account_key or os.getenv("GEE_SERVICE_ACCOUNT_KEY")
        project_id = project or os.getenv("GEE_PROJECT") or "data-visualization-project"
        service_account_email = os.getenv("GEE_SERVICE_ACCOUNT_EMAIL")

        # If no explicit SA email was provided, try to read it from the key file
        if not service_account_email and key_path and Path(key_path).exists():
            try:
                with open(key_path, "r", encoding="utf-8") as f:
                    key_data = json.load(f)
                    service_account_email = key_data.get("client_email")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not read service account email from key file: %s", exc)

        try:
            if key_path:
                if not service_account_email:
                    raise ValueError("Service account email missing for GEE credentials")

                credentials = ee.ServiceAccountCredentials(
                    service_account=service_account_email,
                    key_file=key_path,
                )
                ee.Initialize(credentials, project=project_id)
            else:
                # Use default credentials with configured project
                ee.Initialize(project=project_id)

            logger.info("Google Earth Engine initialized successfully with project: %s", project_id)
        except Exception as e:
            logger.error(f"Failed to initialize GEE: {e}")
            logger.info("Tip: Sign up at https://earthengine.google.com/signup/ if you haven't already")
            raise
    
    def get_weather_data(
        self, 
        region: ee.Geometry,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Fetch weather data from ERA5 or GRIDMET
        
        Args:
            region: Geographic region of interest
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with weather metrics
        """
        try:
            # Use GRIDMET for US data (higher resolution)
            weather = ee.ImageCollection('IDAHO_EPSCOR/GRIDMET') \
                .filterDate(start_date, end_date) \
                .filterBounds(region)
            
            # Extract key wildfire-related variables
            temperature = weather.select('tmmx').mean()  # Max temperature
            humidity = weather.select('rmin').mean()     # Min relative humidity
            wind_speed = weather.select('vs').mean()     # Wind speed
            precipitation = weather.select('pr').sum()   # Total precipitation
            
            # Calculate Fire Weather Index components
            fwi_data = self._calculate_fwi(weather)
            
            # Sample the data over the region
            stats = temperature.addBands([humidity, wind_speed, precipitation]) \
                .reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=region,
                    scale=4000,  # 4km resolution
                    maxPixels=1e9
                ).getInfo()
            
            return {
                'temperature_max': stats.get('tmmx', None),
                'humidity_min': stats.get('rmin', None),
                'wind_speed': stats.get('vs', None),
                'precipitation': stats.get('pr', None),
                'fwi': fwi_data,
                'source': 'GRIDMET',
                'resolution': '4km'
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {}
    
    def get_vegetation_indices(
        self,
        region: ee.Geometry,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Calculate vegetation indices (NDVI, EVI) from satellite imagery
        
        Args:
            region: Geographic region
            start_date: Start date
            end_date: End date
            
        Returns:
            Vegetation index statistics
        """
        try:
            # Use Sentinel-2 for recent high-resolution data
            sentinel = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterDate(start_date, end_date) \
                .filterBounds(region) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
            
            # Calculate NDVI
            def add_ndvi(image):
                ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
                return image.addBands(ndvi)
            
            # Calculate EVI (Enhanced Vegetation Index)
            def add_evi(image):
                evi = image.expression(
                    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                    {
                        'NIR': image.select('B8'),
                        'RED': image.select('B4'),
                        'BLUE': image.select('B2')
                    }
                ).rename('EVI')
                return image.addBands(evi)
            
            # Process collection
            vegetation = sentinel.map(add_ndvi).map(add_evi)
            
            # Get mean values
            ndvi_mean = vegetation.select('NDVI').mean()
            evi_mean = vegetation.select('EVI').mean()
            
            stats = ndvi_mean.addBands(evi_mean) \
                .reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=region,
                    scale=10,  # 10m resolution
                    maxPixels=1e9
                ).getInfo()
            
            return {
                'ndvi': stats.get('NDVI', None),
                'evi': stats.get('EVI', None),
                'source': 'Sentinel-2',
                'resolution': '10m'
            }
            
        except Exception as e:
            logger.error(f"Error calculating vegetation indices: {e}")
            return {}
    
    def get_elevation_slope(
        self,
        region: ee.Geometry
    ) -> Dict:
        """
        Get elevation and slope data from SRTM
        
        Args:
            region: Geographic region
            
        Returns:
            Terrain statistics
        """
        try:
            # SRTM Digital Elevation Model
            srtm = ee.Image('USGS/SRTMGL1_003')
            elevation = srtm.select('elevation')
            
            # Calculate slope
            slope = ee.Terrain.slope(elevation)
            
            # Calculate aspect
            aspect = ee.Terrain.aspect(elevation)
            
            stats = elevation.addBands([slope, aspect]) \
                .reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=region,
                    scale=30,  # 30m resolution
                    maxPixels=1e9
                ).getInfo()
            
            return {
                'elevation': stats.get('elevation', None),
                'slope': stats.get('slope', None),
                'aspect': stats.get('aspect', None),
                'source': 'SRTM',
                'resolution': '30m'
            }
            
        except Exception as e:
            logger.error(f"Error fetching terrain data: {e}")
            return {}
    
    def get_fire_history(
        self,
        region: ee.Geometry,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Get historical fire data from MODIS or VIIRS
        
        Args:
            region: Geographic region
            start_date: Start date
            end_date: End date
            
        Returns:
            Fire history statistics
        """
        try:
            # MODIS Fire Product
            fires = ee.ImageCollection('MODIS/006/MOD14A1') \
                .filterDate(start_date, end_date) \
                .filterBounds(region)
            
            # Count fire detections
            fire_count = fires.select('FireMask').count()
            
            # Get max fire radiative power
            max_frp = fires.select('MaxFRP').max()
            
            stats = fire_count.addBands(max_frp) \
                .reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=region,
                    scale=1000,  # 1km resolution
                    maxPixels=1e9
                ).getInfo()
            
            return {
                'fire_count': stats.get('FireMask', 0),
                'max_fire_power': stats.get('MaxFRP', 0),
                'source': 'MODIS',
                'resolution': '1km'
            }
            
        except Exception as e:
            logger.error(f"Error fetching fire history: {e}")
            return {}
    
    def _calculate_fwi(self, weather_collection: ee.ImageCollection) -> Dict:
        """
        Calculate Fire Weather Index components
        
        Args:
            weather_collection: Weather data collection
            
        Returns:
            FWI components
        """
        # Simplified FWI calculation
        # Full implementation would include FFMC, DMC, DC, ISI, BUI, FWI
        # This is a placeholder for the actual calculation
        return {
            'fwi': None,  # Fire Weather Index
            'note': 'Full FWI calculation requires temporal integration'
        }
    
    def fetch_complete_dataset(
        self,
        latitude: float,
        longitude: float,
        buffer_km: float = 50,
        days_back: int = 30
    ) -> Dict:
        """
        Fetch complete dataset for a location
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            buffer_km: Buffer radius in kilometers
            days_back: Number of days to look back
            
        Returns:
            Complete feature dictionary
        """
        # Create region of interest
        point = ee.Geometry.Point([longitude, latitude])
        region = point.buffer(buffer_km * 1000)  # Convert to meters
        
        # Calculate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"Fetching data for ({latitude}, {longitude}) from {start_str} to {end_str}")
        
        # Fetch all datasets
        weather = self.get_weather_data(region, start_str, end_str)
        vegetation = self.get_vegetation_indices(region, start_str, end_str)
        terrain = self.get_elevation_slope(region)
        fire_history = self.get_fire_history(region, start_str, end_str)
        
        return {
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'buffer_km': buffer_km
            },
            'period': {
                'start': start_str,
                'end': end_str,
                'days': days_back
            },
            'weather': weather,
            'vegetation': vegetation,
            'terrain': terrain,
            'fire_history': fire_history,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Example usage"""
    # Initialize pipeline
    pipeline = GEEDataPipeline()
    
    # Fetch data for California wildfire region
    data = pipeline.fetch_complete_dataset(
        latitude=35.25,
        longitude=-120.25,
        buffer_km=50,
        days_back=30
    )
    
    # Print results
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
