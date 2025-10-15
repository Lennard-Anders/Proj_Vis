"""
Bundle model, calibration, ranges, and surrogate
"""
import shutil
import json
from pathlib import Path


def bundle_model(
    booster_path: str,
    calibration_path: str,
    ranges_path: str,
    surrogate_path: str,
    output_dir: str
):
    """
    Package all model components into a bundle.
    
    Args:
        booster_path: Path to booster file
        calibration_path: Path to calibration JSON
        ranges_path: Path to training ranges JSON
        surrogate_path: Path to surrogate model
        output_dir: Output bundle directory
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    if Path(booster_path).exists():
        shutil.copy(booster_path, output / 'booster.bin')
        print(f"Copied booster")
    
    if Path(calibration_path).exists():
        shutil.copy(calibration_path, output / 'calibration.json')
        print(f"Copied calibration")
    
    if Path(ranges_path).exists():
        shutil.copy(ranges_path, output / 'training_ranges.json')
        print(f"Copied training ranges")
    
    if Path(surrogate_path).exists():
        shutil.copy(surrogate_path, output / 'surrogate.joblib')
        print(f"Copied surrogate")
    
    # Create feature order file
    feature_order = [
        'wind_speed_10m', 'wind_dir_sin', 'wind_dir_cos',
        'gust_10m', 't2m', 'dewpoint', 'rh', 'vpd',
        'rain_24h', 'rain_72h', 'recent_fires_72h_20km',
        'month', 'clim_mean', 'clim_amp'
    ]
    
    with open(output / 'feature_order.json', 'w') as f:
        json.dump(feature_order, f, indent=2)
    
    print(f"Created feature order")
    
    # Create manifest
    manifest = {
        'version': '0.1.0',
        'files': {
            'booster': 'booster.bin',
            'calibration': 'calibration.json',
            'training_ranges': 'training_ranges.json',
            'feature_order': 'feature_order.json',
            'surrogate': 'surrogate.joblib'
        }
    }
    
    with open(output / 'manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nModel bundle created at {output}")


if __name__ == "__main__":
    print("Model Bundle Script")
    print("TODO: Add CLI with argparse")
    
    # Example
    bundle_model(
        booster_path='/tmp/model_output/booster.txt',
        calibration_path='/tmp/calibration.json',
        ranges_path='/tmp/training_ranges.json',
        surrogate_path='/tmp/surrogate.joblib',
        output_dir='/tmp/model_bundle'
    )
