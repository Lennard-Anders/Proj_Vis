"""
Labeler - create ignition events and mine negatives from FDCF
"""
import pandas as pd
import numpy as np
from typing import List


def make_ignition_labels(fdcf_tiles: pd.DataFrame) -> pd.DataFrame:
    """
    Create ignition labels from FDCF tiles.
    
    Identifies first occurrence of fire (mask ∈ {10, 11, 30, 31}) per cell-day.
    
    Args:
        fdcf_tiles: DataFrame from ee_fdcf_ingest.to_daily_tiles
    
    Returns:
        DataFrame with ignition labels (1 = ignition, 0 = no fire)
    """
    # Filter to fire masks only
    fire_masks = [10, 11, 30, 31]
    
    # For this stub, we'll generate labels based on tile detections
    labels = fdcf_tiles.copy()
    labels['ignition'] = (labels['n_detections'] > 0).astype(int)
    
    # Convert tile indices back to lat/lon
    resolution = 0.25
    labels['lat'] = labels['tile_lat'] * resolution + resolution / 2
    labels['lon'] = labels['tile_lon'] * resolution + resolution / 2
    
    return labels[['date', 'lat', 'lon', 'ignition']]


def mine_hard_negatives(
    labels: pd.DataFrame,
    weather: pd.DataFrame,
    ratio: int = 10
) -> pd.DataFrame:
    """
    Mine hard negatives - locations with high risk but no fire.
    
    Args:
        labels: DataFrame with ignition labels
        weather: DataFrame with weather features
        ratio: Ratio of negatives to positives
    
    Returns:
        DataFrame with balanced positives and hard negatives
    """
    # Merge labels with weather to get features
    merged = pd.merge(
        weather,
        labels,
        on=['date', 'lat', 'lon'],
        how='left'
    )
    
    # Fill missing ignition labels with 0 (no fire)
    merged['ignition'] = merged['ignition'].fillna(0).astype(int)
    
    # Split positives and negatives
    positives = merged[merged['ignition'] == 1]
    negatives = merged[merged['ignition'] == 0]
    
    # Hard negative mining based on features
    # Select negatives with high wind speed, low RH, low rain
    if len(negatives) > 0:
        negatives['risk_score'] = (
            negatives['wind_speed_10m'] / 30.0 +
            (100 - negatives['rh']) / 100.0 +
            (1.0 / (negatives['precipitation'] + 0.1))
        )
        
        # Sort by risk score and take top hard negatives
        negatives = negatives.sort_values('risk_score', ascending=False)
        n_hard_negatives = min(len(positives) * ratio, len(negatives))
        hard_negatives = negatives.head(n_hard_negatives)
    else:
        hard_negatives = negatives
    
    # Combine positives and hard negatives
    balanced = pd.concat([positives, hard_negatives], ignore_index=True)
    
    # Shuffle
    balanced = balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return balanced


def add_temporal_context(
    labels: pd.DataFrame,
    lookback_days: List[int] = [3, 7]
) -> pd.DataFrame:
    """
    Add temporal context (lagged fire occurrences).
    
    Args:
        labels: DataFrame with ignition labels
        lookback_days: List of lookback periods
    
    Returns:
        DataFrame with lagged features
    """
    # Sort by location and date
    labels = labels.sort_values(['lat', 'lon', 'date'])
    
    for lag in lookback_days:
        labels[f'fires_last_{lag}d'] = 0  # Stub
    
    return labels


if __name__ == "__main__":
    print("Labeler Script")
    print("TODO: Add CLI for processing date ranges")
    
    # Example
    from ee_fdcf_ingest import fetch_fdcf, to_daily_tiles
    from weather_ingest import fetch_reanalysis, enrich_weather_data
    
    bbox = (-125, 32, -114, 42)
    date = "2024-01-15"
    
    # Fetch FDCF
    fdcf = fetch_fdcf(bbox, date)
    tiles = to_daily_tiles(fdcf)
    
    # Make labels
    labels = make_ignition_labels(tiles)
    print(f"Created {len(labels)} labels ({labels['ignition'].sum()} positives)")
    
    # Fetch weather
    weather = fetch_reanalysis(bbox, date, date)
    weather = enrich_weather_data(weather)
    
    # Mine hard negatives
    balanced = mine_hard_negatives(labels, weather)
    print(f"Balanced dataset: {len(balanced)} samples")
