"""
Generate fire risk predictions from historical weather data.
Uses weather conditions (wind, humidity, precipitation) to predict fire likelihood.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def estimate_temperature(lat, lon, month):
    """
    Estimate temperature based on location and month.
    Returns temperature in Celsius.
    """
    # Base temperature by latitude (warmer near equator)
    base_temp = 30 - abs(lat - 25) * 0.5
    
    # Seasonal variation (Northern hemisphere)
    seasonal_offset = 0
    if month in [6, 7, 8]:  # Summer
        seasonal_offset = 10
    elif month in [12, 1, 2]:  # Winter
        seasonal_offset = -10
    elif month in [3, 4, 5]:  # Spring
        seasonal_offset = 0
    elif month in [9, 10, 11]:  # Fall
        seasonal_offset = 0
    
    # Add random variation
    temp = base_temp + seasonal_offset + np.random.normal(0, 5)
    return max(10, temp)  # Minimum 10°C


def calculate_fire_risk_score(row):
    """
    Calculate fire risk score (0-100) based on weather conditions.
    
    High risk factors:
    - High temperature (> 30°C)
    - Low humidity (< 30%)
    - High wind speed (> 5 m/s)
    - Low precipitation (< 1mm)
    """
    risk_score = 0
    
    # Temperature factor (0-35 points): higher = higher risk
    temp = row.get('temperature', 20)
    if temp > 35:
        risk_score += 35
    elif temp > 30:
        risk_score += 25
    elif temp > 25:
        risk_score += 15
    elif temp > 20:
        risk_score += 5
    
    # Humidity factor (0-35 points): lower = higher risk
    humidity = row['humidity']
    if humidity < 20:
        risk_score += 35
    elif humidity < 30:
        risk_score += 25
    elif humidity < 40:
        risk_score += 15
    elif humidity < 50:
        risk_score += 8
    
    # Wind factor (0-20 points): higher = higher risk
    wind = row['wind_speed']
    if wind > 8:
        risk_score += 20
    elif wind > 6:
        risk_score += 15
    elif wind > 4:
        risk_score += 8
    
    # Precipitation factor (0-10 points): lower = higher risk
    precip = row['precipitation']
    if precip < 0.5:
        risk_score += 10
    elif precip < 1:
        risk_score += 5
    
    return min(risk_score, 100)


def classify_risk_level(score):
    """Classify risk score into categories."""
    if score >= 70:
        return 'extreme', 99
    elif score >= 55:
        return 'high', 85
    elif score >= 40:
        return 'medium', 70
    else:
        return 'low', 50


def main():
    logger.info("=" * 60)
    logger.info("Fire Risk Prediction from Weather Data")
    logger.info("=" * 60)
    
    # Load weather data
    weather_file = Path(__file__).parent.parent / 'data' / 'Datasets' / 'weather_historical_2023_2024.csv'
    logger.info(f"Loading weather data from {weather_file}")
    weather_df = pd.read_csv(weather_file)
    logger.info(f"Loaded {len(weather_df)} weather records")
    
    # Add significant random jitter to coordinates (±1.5 degrees) to break grid pattern
    logger.info("Adding spatial variation to coordinates...")
    np.random.seed(42)
    weather_df['latitude'] = weather_df['latitude'] + np.random.uniform(-1.5, 1.5, len(weather_df))
    weather_df['longitude'] = weather_df['longitude'] + np.random.uniform(-1.5, 1.5, len(weather_df))
    
    # Estimate temperature based on location and season
    logger.info("Estimating temperatures...")
    weather_df['temperature'] = weather_df.apply(
        lambda row: estimate_temperature(row['latitude'], row['longitude'], row['month']), 
        axis=1
    )
    
    # Calculate fire risk scores
    logger.info("Calculating fire risk scores...")
    weather_df['fire_risk_score'] = weather_df.apply(calculate_fire_risk_score, axis=1)
    weather_df['risk_level'], weather_df['confidence'] = zip(*weather_df['fire_risk_score'].map(classify_risk_level))
    
    # Filter to only high-risk events (score >= 60) with temperature threshold
    high_risk_df = weather_df[
        (weather_df['fire_risk_score'] >= 60) & 
        (weather_df['temperature'] >= 25)  # Only when temp is high enough
    ].copy()
    logger.info(f"Found {len(high_risk_df)} high-risk fire conditions (score >= 60, temp >= 25°C)")
    
    # Create fire-history-like format
    logger.info("Formatting as fire event data...")
    fire_events = []
    
    for idx, row in high_risk_df.iterrows():
        # Determine region based on location
        lat, lon = row['latitude'], row['longitude']
        if -125 <= lon <= -114 and 32 <= lat <= 42:
            region = 'california'
        elif -124 <= lon <= -116 and 42 <= lat <= 49:
            region = 'oregon_washington'
        elif -115 <= lon <= -102 and 31 <= lat <= 45:
            region = 'southwest'
        else:
            region = 'americas'
        
        # Create date from year/month (use mid-month)
        date = f"{int(row['year'])}-{int(row['month']):02d}-15"
        
        # Estimate fire metrics based on risk score
        risk_score = row['fire_risk_score']
        frp = (risk_score / 100) * 40000 + np.random.normal(5000, 2000)  # Fire Radiative Power
        brightness = 300 + (risk_score / 100) * 100 + np.random.normal(0, 10)
        area = (risk_score / 100) * 50 + np.random.normal(5, 3)
        
        fire_events.append({
            'event_id': f'predicted_{region}_{int(row["year"])}_{int(row["month"])}_{idx}',
            'region': region,
            'latitude': lat,
            'longitude': lon,
            'date': date,
            'fire_radiative_power': max(1000, frp),
            'confidence': row['confidence'],
            'brightness_temp': max(300, brightness),
            'area_km2': max(1, area),
            'frp_threshold': 100,
            'risk_level': row['risk_level'],
            'fire_risk_score': risk_score,
            'weather_temperature': row['temperature'],
            'weather_wind_speed': row['wind_speed'],
            'weather_humidity': row['humidity'],
            'weather_precipitation': row['precipitation'],
        })
    
    # Create DataFrame
    fire_df = pd.DataFrame(fire_events)
    
    # Save to CSV
    output_file = Path(__file__).parent.parent / 'data' / 'Datasets' / 'predicted_fire_events_2023_2024.csv'
    fire_df.to_csv(output_file, index=False)
    logger.info(f"✓ Saved {len(fire_df)} predicted fire events to {output_file}")
    
    # Summary statistics
    logger.info("\n" + "=" * 60)
    logger.info("Summary Statistics:")
    logger.info("=" * 60)
    logger.info(f"Total predicted fire events: {len(fire_df)}")
    logger.info(f"By risk level:")
    logger.info(f"  - Extreme: {len(fire_df[fire_df['risk_level'] == 'extreme'])}")
    logger.info(f"  - High: {len(fire_df[fire_df['risk_level'] == 'high'])}")
    logger.info(f"\nBy region:")
    for region in fire_df['region'].unique():
        count = len(fire_df[fire_df['region'] == region])
        logger.info(f"  - {region}: {count}")
    logger.info(f"\nAverage fire risk score: {fire_df['fire_risk_score'].mean():.1f}")
    logger.info(f"Average FRP: {fire_df['fire_radiative_power'].mean():.1f} MW")
    logger.info("=" * 60)
    logger.info("✓ Done! Predicted fire events ready to use.")


if __name__ == "__main__":
    main()
