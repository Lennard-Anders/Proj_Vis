"""
Fetch real-time weather data from Google Earth Engine and save to CSV.
Run this script periodically to update the weather data cache.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from etl.gee_connector import GEEDataPipeline
import ee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_and_save_weather_data(output_dir: Path):
    """Fetch weather data from GEE and save to CSV files."""
    
    try:
        # Initialize GEE
        logger.info("Initializing Google Earth Engine...")
        gee = GEEDataPipeline()
        
        # Use a recent date that has GRIDMET data (GRIDMET typically lags by a few days)
        # Use 2024-12-31 as a recent date with available data
        data_date = '2024-12-31'
        logger.info(f"Fetching weather data for: {data_date}")
        
        # Define Americas region
        bbox = {'min_lat': 25, 'max_lat': 50, 'min_lon': -125, 'max_lon': -70}
        region = ee.Geometry.Rectangle([
            bbox['min_lon'], bbox['min_lat'],
            bbox['max_lon'], bbox['max_lat']
        ])
        
        # Fetch GRIDMET data
        logger.info("Querying GRIDMET dataset...")
        next_date = (datetime.strptime(data_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        gridmet = ee.ImageCollection('IDAHO_EPSCOR/GRIDMET') \
            .filterDate(data_date, next_date) \
            .filterBounds(region) \
            .first()
        
        if not gridmet:
            logger.error("No GRIDMET data available for this date")
            return False
        
        # Generate sampling grid (1.5 degree spacing for good coverage)
        logger.info("Generating sampling grid...")
        lats = [lat for lat in range(25, 51, 2)]  # Every 2 degrees
        lons = [lon for lon in range(-125, -69, 2)]
        
        sample_points = []
        for lat in lats:
            for lon in lons:
                # Land filter
                if lon < -125 or lon > -70 or (lat < 26 and -100 < lon < -80):
                    continue
                sample_points.append(ee.Feature(ee.Geometry.Point([lon, lat])))
        
        logger.info(f"Sampling {len(sample_points)} points across Americas...")
        points_fc = ee.FeatureCollection(sample_points)
        
        # === WIND DATA ===
        logger.info("Fetching wind speed data...")
        wind_image = gridmet.select('vs')
        wind_samples = wind_image.sampleRegions(
            collection=points_fc,
            scale=8000,
            geometries=True
        ).getInfo()
        
        wind_data = []
        for feature in wind_samples.get('features', []):
            props = feature.get('properties', {})
            coords = feature.get('geometry', {}).get('coordinates', [])
            if props.get('vs') is not None and len(coords) == 2:
                wind_data.append({
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'wind_speed': props['vs']
                })
        
        wind_df = pd.DataFrame(wind_data)
        wind_file = output_dir / 'wind_current.csv'
        wind_df.to_csv(wind_file, index=False)
        logger.info(f"✓ Saved {len(wind_data)} wind points to {wind_file}")
        
        # === HUMIDITY DATA ===
        logger.info("Fetching humidity data...")
        humidity_image = gridmet.select('rmin')
        humidity_samples = humidity_image.sampleRegions(
            collection=points_fc,
            scale=8000,
            geometries=True
        ).getInfo()
        
        humidity_data = []
        for feature in humidity_samples.get('features', []):
            props = feature.get('properties', {})
            coords = feature.get('geometry', {}).get('coordinates', [])
            if props.get('rmin') is not None and len(coords) == 2:
                humidity_data.append({
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'humidity': props['rmin']
                })
        
        humidity_df = pd.DataFrame(humidity_data)
        humidity_file = output_dir / 'humidity_current.csv'
        humidity_df.to_csv(humidity_file, index=False)
        logger.info(f"✓ Saved {len(humidity_data)} humidity points to {humidity_file}")
        
        # === RAIN DATA ===
        logger.info("Fetching precipitation data...")
        rain_image = gridmet.select('pr')
        rain_samples = rain_image.sampleRegions(
            collection=points_fc,
            scale=8000,
            geometries=True
        ).getInfo()
        
        rain_data = []
        for feature in rain_samples.get('features', []):
            props = feature.get('properties', {})
            coords = feature.get('geometry', {}).get('coordinates', [])
            if props.get('pr') is not None and len(coords) == 2:
                rain_data.append({
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'rain': props['pr']
                })
        
        rain_df = pd.DataFrame(rain_data)
        rain_file = output_dir / 'rain_current.csv'
        rain_df.to_csv(rain_file, index=False)
        logger.info(f"✓ Saved {len(rain_data)} rain points to {rain_file}")
        
        # Save metadata
        metadata = {
            'last_updated': datetime.now().isoformat(),
            'data_date': data_date,
            'wind_points': len(wind_data),
            'humidity_points': len(humidity_data),
            'rain_points': len(rain_data)
        }
        metadata_df = pd.DataFrame([metadata])
        metadata_file = output_dir / 'weather_metadata.csv'
        metadata_df.to_csv(metadata_file, index=False)
        logger.info(f"✓ Saved metadata to {metadata_file}")
        
        logger.info(f"\n🎉 Successfully fetched and saved all weather data!")
        logger.info(f"   Wind: {len(wind_data)} points")
        logger.info(f"   Humidity: {len(humidity_data)} points")
        logger.info(f"   Rain: {len(rain_data)} points")
        logger.info(f"   Data date: {data_date}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # Output directory
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("Weather Data Fetcher - Google Earth Engine to CSV")
    logger.info("=" * 60)
    
    success = fetch_and_save_weather_data(data_dir)
    
    if success:
        logger.info("\n✓ All done! Weather CSVs are ready to use.")
        sys.exit(0)
    else:
        logger.error("\n✗ Failed to fetch weather data.")
        sys.exit(1)
