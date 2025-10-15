"""
Weather data ingestion (ERA5, Open-Meteo, NWS)
"""
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict
from datetime import datetime, timedelta


def fetch_reanalysis(
    bbox: Tuple[float, float, float, float],
    date_start: str,
    date_end: str,
    variables: List[str] = None
) -> pd.DataFrame:
    """
    Fetch reanalysis weather data (ERA5, Open-Meteo).
    
    Args:
        bbox: (min_lon, min_lat, max_lon, max_lat)
        date_start: Start date (YYYY-MM-DD)
        date_end: End date (YYYY-MM-DD)
        variables: List of variable names
    
    Returns:
        DataFrame with weather data on 0.25° grid
    
    TODO: Replace with actual API calls to ERA5/Open-Meteo
    """
    if variables is None:
        variables = [
            't2m', 'dewpoint', 'u10', 'v10',
            'gust_10m', 'precipitation'
        ]
    
    # Stub: generate synthetic data
    min_lon, min_lat, max_lon, max_lat = bbox
    resolution = 0.25
    
    lats = np.arange(min_lat, max_lat, resolution)
    lons = np.arange(min_lon, max_lon, resolution)
    
    dates = pd.date_range(date_start, date_end, freq='D')
    
    data = []
    for date in dates:
        for lat in lats:
            for lon in lons:
                row = {
                    'date': date.date(),
                    'lat': lat,
                    'lon': lon,
                    't2m': np.random.uniform(280, 310),
                    'dewpoint': np.random.uniform(270, 300),
                    'u10': np.random.uniform(-10, 10),
                    'v10': np.random.uniform(-10, 10),
                    'gust_10m': np.random.uniform(0, 25),
                    'precipitation': np.random.exponential(2.0)
                }
                data.append(row)
    
    df = pd.DataFrame(data)
    return df


def compute_rh_vpd(t2m: float, dewpoint: float) -> Tuple[float, float]:
    """
    Compute relative humidity and vapor pressure deficit.
    
    Args:
        t2m: Temperature at 2m (Kelvin)
        dewpoint: Dewpoint temperature (Kelvin)
    
    Returns:
        Tuple of (rh, vpd) where rh is in % and vpd is in kPa
    """
    # Saturation vapor pressure (Tetens formula)
    def es(T_K):
        T_C = T_K - 273.15
        return 0.6108 * np.exp((17.27 * T_C) / (T_C + 237.3))
    
    es_t2m = es(t2m)
    es_dew = es(dewpoint)
    
    # Relative humidity
    rh = (es_dew / es_t2m) * 100.0
    rh = np.clip(rh, 0, 100)
    
    # Vapor pressure deficit
    vpd = es_t2m - es_dew
    
    return rh, vpd


def compute_wind_components(u10: float, v10: float) -> Dict[str, float]:
    """
    Compute wind speed and direction from components.
    
    Args:
        u10: U-component of wind (m/s)
        v10: V-component of wind (m/s)
    
    Returns:
        Dictionary with wind_speed_10m, wind_dir, wind_dir_sin, wind_dir_cos
    """
    wind_speed = np.sqrt(u10**2 + v10**2)
    wind_dir = np.arctan2(u10, v10)  # Radians
    
    return {
        'wind_speed_10m': wind_speed,
        'wind_dir': wind_dir,
        'wind_dir_sin': np.sin(wind_dir),
        'wind_dir_cos': np.cos(wind_dir)
    }


def enrich_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich weather data with derived variables (RH, VPD, wind components).
    
    Args:
        df: DataFrame from fetch_reanalysis
    
    Returns:
        Enriched DataFrame
    """
    # Compute RH and VPD
    df['rh'], df['vpd'] = zip(*df.apply(
        lambda row: compute_rh_vpd(row['t2m'], row['dewpoint']),
        axis=1
    ))
    
    # Compute wind components
    wind_data = df.apply(
        lambda row: compute_wind_components(row['u10'], row['v10']),
        axis=1
    )
    
    for key in ['wind_speed_10m', 'wind_dir', 'wind_dir_sin', 'wind_dir_cos']:
        df[key] = wind_data.apply(lambda x: x[key])
    
    return df


if __name__ == "__main__":
    print("Weather Ingestion Script")
    print("TODO: Add CLI for fetching date ranges")
    
    # Example
    bbox = (-125, 32, -114, 42)
    df = fetch_reanalysis(bbox, "2024-01-01", "2024-01-07")
    print(f"Fetched {len(df)} weather records")
    
    df = enrich_weather_data(df)
    print(f"Enriched with RH, VPD, wind components")
