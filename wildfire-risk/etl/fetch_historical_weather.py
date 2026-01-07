"""
Fetch historical weather data from GEE for 2 years and save to CSV.
Parameters: wind speed, humidity, precipitation from GRIDMET.
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import ee

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.gee_connector import GEEDataPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_monthly_weather_data(year, month):
    """Fetch weather data for a specific month using the proven sampleRegions approach."""
    # Create date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    logger.info(f"Fetching data for {year}-{month:02d} ({start_str} to {end_str})")
    
    try:
        # Get GRIDMET collection for the month (monthly average)
        gridmet = ee.ImageCollection('IDAHO_EPSCOR/GRIDMET') \
            .filterDate(start_str, end_str) \
            .mean()
        
        # Generate sampling grid
        lats = [lat for lat in range(25, 51, 2)]
        lons = [lon for lon in range(-125, -69, 2)]
        
        sample_points = []
        for lat in lats:
            for lon in lons:
                sample_points.append(ee.Feature(ee.Geometry.Point([lon, lat])))
        
        points_fc = ee.FeatureCollection(sample_points)
        
        # Sample all three parameters at once
        samples = gridmet.select(['vs', 'rmin', 'pr']).sampleRegions(
            collection=points_fc,
            scale=8000,
            geometries=True
        ).getInfo()
        
        # Extract data
        monthly_data = []
        for feature in samples.get('features', []):
            props = feature.get('properties', {})
            coords = feature.get('geometry', {}).get('coordinates', [])
            if len(coords) == 2:
                monthly_data.append({
                    'year': year,
                    'month': month,
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'wind_speed': props.get('vs'),
                    'humidity': props.get('rmin'),
                    'precipitation': props.get('pr'),
                })
        
        logger.info(f"✓ Fetched {len(monthly_data)} points for {year}-{month:02d}")
        return monthly_data
        
    except Exception as e:
        logger.error(f"✗ Failed for {year}-{month:02d}: {e}")
        return []


def main():
    logger.info("=" * 60)
    logger.info("Historical Weather Data Fetcher - 2 Years")
    logger.info("=" * 60)
    
    # Initialize GEE
    logger.info("Initializing Google Earth Engine...")
    pipeline = GEEDataPipeline(project='data-visuaization-project')
    
    # Fetch data for 2 years (2023-2024)
    all_data = []
    
    for year in [2023, 2024]:
        for month in range(1, 13):
            monthly_data = fetch_monthly_weather_data(year, month)
            all_data.extend(monthly_data)
            
            # Save checkpoint every 3 months
            if month % 3 == 0:
                logger.info(f"Checkpoint: {len(all_data)} total records so far")
    
    # Create DataFrame
    logger.info(f"Creating DataFrame with {len(all_data)} records...")
    
    if len(all_data) == 0:
        logger.error("No data fetched! Exiting.")
        return
    
    df = pd.DataFrame(all_data)
    
    # Save to CSV in data/Datasets folder
    output_dir = Path(__file__).parent.parent / 'data' / 'Datasets'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'weather_historical_2023_2024.csv'
    df.to_csv(output_file, index=False)
    logger.info(f"✓ Saved historical weather data to {output_file}")
    
    # Print summary statistics
    logger.info("\n" + "=" * 60)
    logger.info("Summary Statistics:")
    logger.info("=" * 60)
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Date range: {df['year'].min()}-{df['month'].min():02d} to {df['year'].max()}-{df['month'].max():02d}")
    logger.info(f"Unique locations: {len(df[['latitude', 'longitude']].drop_duplicates())}")
    logger.info(f"\nWind Speed - min: {df['wind_speed'].min():.2f}, max: {df['wind_speed'].max():.2f}, mean: {df['wind_speed'].mean():.2f}")
    logger.info(f"Humidity - min: {df['humidity'].min():.2f}, max: {df['humidity'].max():.2f}, mean: {df['humidity'].mean():.2f}")
    logger.info(f"Precipitation - min: {df['precipitation'].min():.2f}, max: {df['precipitation'].max():.2f}, mean: {df['precipitation'].mean():.2f}")
    logger.info("=" * 60)
    logger.info("✓ All done!")


if __name__ == "__main__":
    main()
