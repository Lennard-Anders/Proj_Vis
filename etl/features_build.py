"""
Feature builder - join labels, weather, climatology to daily 0.25° grid
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def join_features(
    labels: pd.DataFrame,
    weather: pd.DataFrame,
    climatology: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Join labels with weather and climatology on 0.25° grid.
    
    Args:
        labels: DataFrame with ignition labels
        weather: DataFrame with weather features
        climatology: Optional DataFrame with climatology
    
    Returns:
        DataFrame with complete feature set
    """
    # Merge labels and weather
    features = pd.merge(
        weather,
        labels,
        on=['date', 'lat', 'lon'],
        how='left'
    )
    
    # Fill missing labels with 0 (no fire)
    features['ignition'] = features['ignition'].fillna(0).astype(int)
    
    # Add climatology if provided
    if climatology is not None:
        features = pd.merge(
            features,
            climatology,
            on=['lat', 'lon'],
            how='left'
        )
    
    return features


def add_spatial_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add spatial features (month, region, etc.).
    
    Args:
        df: DataFrame with date, lat, lon
    
    Returns:
        DataFrame with spatial features
    """
    # Extract month
    df['month'] = pd.to_datetime(df['date']).dt.month
    
    # Assign region based on lat/lon (simplified)
    # TODO: Use actual region boundaries
    df['region_id'] = 0
    df.loc[df['lat'] > 40, 'region_id'] = 1  # North
    df.loc[df['lat'] < 35, 'region_id'] = 2  # South
    
    return df


def add_lagged_features(
    df: pd.DataFrame,
    lags: Dict[str, int] = None
) -> pd.DataFrame:
    """
    Add lagged features (rain_24h, rain_72h, recent_fires_72h).
    
    Args:
        df: DataFrame with features
        lags: Dictionary mapping feature to lag period (hours)
    
    Returns:
        DataFrame with lagged features
    """
    if lags is None:
        lags = {
            'precipitation': [24, 72],
            'ignition': [72]
        }
    
    # Sort by location and date
    df = df.sort_values(['lat', 'lon', 'date'])
    
    # Add lagged precipitation (cumulative)
    if 'precipitation' in lags:
        for lag_hours in lags['precipitation']:
            lag_days = lag_hours // 24
            col_name = f'rain_{lag_hours}h'
            
            # Stub: just copy precipitation for now
            # TODO: Implement actual rolling sum
            df[col_name] = df['precipitation']
    
    # Add recent fires within 20km
    if 'ignition' in lags:
        # Stub: simplified count
        df['recent_fires_72h_20km'] = 0
    
    return df


def add_climatology_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add climatology features (mean, amplitude, anomalies).
    
    Args:
        df: DataFrame with weather features
    
    Returns:
        DataFrame with climatology features
    """
    # Stub: generate synthetic climatology
    df['clim_mean'] = 295.0  # Mean temperature
    df['clim_amp'] = 10.0    # Seasonal amplitude
    
    # Temperature anomaly
    df['t2m_anomaly'] = df['t2m'] - df['clim_mean']
    
    return df


def build_features(
    labels: pd.DataFrame,
    weather: pd.DataFrame,
    output_path: str = None
) -> pd.DataFrame:
    """
    Build complete feature set for training.
    
    Args:
        labels: DataFrame with ignition labels
        weather: DataFrame with weather data
        output_path: Optional path to save Parquet
    
    Returns:
        DataFrame with complete feature set
    """
    # Join base features
    features = join_features(labels, weather)
    
    # Add spatial features
    features = add_spatial_features(features)
    
    # Add lagged features
    features = add_lagged_features(features)
    
    # Add climatology
    features = add_climatology_features(features)
    
    # Select final columns (following data contract)
    final_columns = [
        # Keys
        'date', 'lat', 'lon',
        # Static
        'month', 'clim_mean', 'clim_amp', 'region_id',
        # Dynamic
        'wind_speed_10m', 'wind_dir_sin', 'wind_dir_cos',
        'gust_10m', 't2m', 'dewpoint', 'rh', 'vpd',
        'rain_24h', 'rain_72h', 'recent_fires_72h_20km',
        # Label
        'ignition',
        # Quality (stub)
    ]
    
    # Add quality stubs
    features['dqf_mask'] = 1
    features['data_availability'] = 0.95
    
    # Rename precipitation columns
    if 'rain_24h' not in features.columns and 'precipitation' in features.columns:
        features['rain_24h'] = features['precipitation']
        features['rain_72h'] = features['precipitation'] * 3
    
    # Select columns that exist
    available_columns = [col for col in final_columns if col in features.columns]
    features = features[available_columns + ['dqf_mask', 'data_availability']]
    
    # Save to Parquet if path provided
    if output_path:
        features.to_parquet(output_path, index=False)
        print(f"Saved features to {output_path}")
    
    return features


if __name__ == "__main__":
    print("Features Build Script")
    print("TODO: Add CLI for processing date ranges")
    
    # Example
    from labeler import make_ignition_labels, mine_hard_negatives
    from weather_ingest import fetch_reanalysis, enrich_weather_data
    from ee_fdcf_ingest import fetch_fdcf, to_daily_tiles
    
    bbox = (-125, 32, -114, 42)
    date = "2024-01-15"
    
    # Build features
    fdcf = fetch_fdcf(bbox, date)
    tiles = to_daily_tiles(fdcf)
    labels = make_ignition_labels(tiles)
    weather = fetch_reanalysis(bbox, date, date)
    weather = enrich_weather_data(weather)
    
    features = build_features(labels, weather)
    print(f"Built {len(features)} feature records")
    print(f"Columns: {list(features.columns)}")
