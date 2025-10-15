"""
Data quality checks and availability masks
"""
import pandas as pd
import numpy as np
from typing import Dict, List


def compute_data_availability(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute data availability per record.
    
    Checks for missing values in critical features.
    
    Args:
        df: DataFrame with features
    
    Returns:
        DataFrame with data_availability column
    """
    critical_features = [
        'wind_speed_10m', 'rh', 't2m', 'precipitation'
    ]
    
    # Count available features
    available = df[critical_features].notna().sum(axis=1)
    total = len(critical_features)
    
    df['data_availability'] = available / total
    
    return df


def compute_dqf_mask(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute data quality flag mask.
    
    Flags:
    - 0: Missing data
    - 1: Good quality
    - 2: Suspicious values
    - 3: Out of range
    
    Args:
        df: DataFrame with features
    
    Returns:
        DataFrame with dqf_mask column
    """
    df['dqf_mask'] = 1  # Default: good quality
    
    # Flag missing data
    df.loc[df['data_availability'] < 0.8, 'dqf_mask'] = 0
    
    # Flag suspicious values
    # Wind speed > 40 m/s
    if 'wind_speed_10m' in df.columns:
        df.loc[df['wind_speed_10m'] > 40, 'dqf_mask'] = 2
    
    # RH > 100% or < 0%
    if 'rh' in df.columns:
        df.loc[(df['rh'] > 100) | (df['rh'] < 0), 'dqf_mask'] = 3
    
    # Temperature out of range (220K - 330K)
    if 't2m' in df.columns:
        df.loc[(df['t2m'] < 220) | (df['t2m'] > 330), 'dqf_mask'] = 3
    
    return df


def generate_quality_report(df: pd.DataFrame) -> Dict:
    """
    Generate quality report for dataset.
    
    Args:
        df: DataFrame with features
    
    Returns:
        Dictionary with quality metrics
    """
    report = {
        'total_records': len(df),
        'date_range': (df['date'].min(), df['date'].max()) if 'date' in df.columns else None,
        'spatial_extent': {
            'lat': (df['lat'].min(), df['lat'].max()) if 'lat' in df.columns else None,
            'lon': (df['lon'].min(), df['lon'].max()) if 'lon' in df.columns else None
        }
    }
    
    # Availability metrics
    if 'data_availability' in df.columns:
        report['availability'] = {
            'mean': df['data_availability'].mean(),
            'min': df['data_availability'].min(),
            'pct_complete': (df['data_availability'] >= 0.95).mean()
        }
    
    # DQF metrics
    if 'dqf_mask' in df.columns:
        report['quality'] = {
            'good': (df['dqf_mask'] == 1).sum(),
            'missing': (df['dqf_mask'] == 0).sum(),
            'suspicious': (df['dqf_mask'] == 2).sum(),
            'out_of_range': (df['dqf_mask'] == 3).sum()
        }
    
    # Feature completeness
    feature_cols = [col for col in df.columns if col not in ['date', 'lat', 'lon']]
    report['feature_completeness'] = {
        col: 1.0 - df[col].isna().mean()
        for col in feature_cols
    }
    
    return report


def filter_by_quality(
    df: pd.DataFrame,
    min_availability: float = 0.8,
    exclude_dqf: List[int] = [0, 3]
) -> pd.DataFrame:
    """
    Filter dataset by quality thresholds.
    
    Args:
        df: DataFrame with quality columns
        min_availability: Minimum data availability
        exclude_dqf: List of DQF values to exclude
    
    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()
    
    # Filter by availability
    if 'data_availability' in filtered.columns:
        filtered = filtered[filtered['data_availability'] >= min_availability]
    
    # Filter by DQF
    if 'dqf_mask' in filtered.columns:
        filtered = filtered[~filtered['dqf_mask'].isin(exclude_dqf)]
    
    return filtered


if __name__ == "__main__":
    print("Data Quality Script")
    
    # Example
    from features_build import build_features
    from labeler import make_ignition_labels
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
    
    # Compute quality
    features = compute_data_availability(features)
    features = compute_dqf_mask(features)
    
    # Generate report
    report = generate_quality_report(features)
    print("\nQuality Report:")
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    # Filter
    filtered = filter_by_quality(features)
    print(f"\nFiltered: {len(filtered)} / {len(features)} records passed quality checks")
