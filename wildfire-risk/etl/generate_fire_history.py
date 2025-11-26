"""
Generate historical wildfire CSV from MODIS satellite data.
This script pre-fetches fire history to avoid slow GEE queries on every request.
"""
import ee
import pandas as pd
from datetime import datetime, timedelta
import json

# Initialize Earth Engine
try:
    ee.Initialize(project='data-visuaization-project')
    print("✅ Earth Engine initialized")
except Exception as e:
    print(f"Error initializing EE: {e}")
    raise

def generate_fire_history_csv(
    regions,
    start_date='2020-01-01',
    end_date='2025-11-26',
    output_file='../data/fire_history.csv'
):
    """
    Generate CSV of historical fires for predefined regions.
    
    Args:
        regions: Dict of region configs {name: {lat, lon, radius_km}}
        start_date: Start date for fire history
        end_date: End date for fire history
        output_file: Path to save CSV
    """
    all_fires = []
    
    for region_name, config in regions.items():
        print(f"\n📍 Processing region: {region_name}")
        print(f"   Center: {config['lat']}, {config['lon']}")
        print(f"   Radius: {config['radius_km']} km")
        
        # Create region geometry
        region = ee.Geometry.Point([config['lon'], config['lat']]).buffer(config['radius_km'] * 1000)
        
        # Fetch MODIS fire data
        collection = ee.ImageCollection('MODIS/061/MOD14A1') \
            .filterDate(start_date, end_date) \
            .filterBounds(region) \
            .select(['MaxFRP', 'QA'])
        
        # Create composite
        composite = collection.max()
        
        # Fire threshold based on region size - HIGHER to avoid false positives
        if config['radius_km'] > 1000:
            frp_threshold = 1000  # Large regions: only major fires (avoid sunlight/water reflections)
            max_samples = 300
            scale = 5000
        else:
            frp_threshold = 100  # Small regions: moderate fires (still filtering out weak signals)
            max_samples = 500
            scale = 1000
        
        # Apply fire mask
        fire_mask = composite.select('MaxFRP').gt(frp_threshold)
        
        # Add land mask to filter ocean false positives
        land_mask = ee.Image('MODIS/006/MCD12Q1/2020_01_01').select('LC_Type1').neq(0)
        
        masked_composite = composite.updateMask(fire_mask).updateMask(land_mask)
        
        # Sample fire pixels
        print(f"   Sampling fires (threshold: {frp_threshold} MW, max: {max_samples})...")
        fire_samples = masked_composite.sample(
            region=region,
            scale=scale,
            numPixels=max_samples,
            seed=42,
            geometries=True
        )
        
        # Get features
        features_list = fire_samples.getInfo()
        
        if not features_list or 'features' not in features_list:
            print(f"   ⚠️  No fires found")
            continue
        
        features = features_list['features']
        print(f"   ✅ Found {len(features)} fires")
        
        # Convert to records
        for idx, feature in enumerate(features):
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            coords = geom.get('coordinates', [0, 0])
            
            # Calculate midpoint date for composite
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            mid_date = start_dt + (end_dt - start_dt) / 2
            
            # Extract confidence from QA bits
            qa_value = int(props.get('QA', 0))
            confidence_bits = (qa_value >> 0) & 0b11
            confidence_map = {0: 0, 1: 33, 2: 66, 3: 99}
            confidence = confidence_map.get(confidence_bits, 0)
            
            fire_record = {
                'event_id': f'fire_{region_name}_{idx}',
                'region': region_name,
                'latitude': coords[1],
                'longitude': coords[0],
                'date': mid_date.strftime('%Y-%m-%d'),
                'fire_radiative_power': float(props.get('MaxFRP', 0)),
                'confidence': confidence,
                'brightness_temp': 0.0,  # Not available in composite
                'area_km2': 1.0,  # Approximate pixel area
                'frp_threshold': frp_threshold,
                'query_start': start_date,
                'query_end': end_date
            }
            
            all_fires.append(fire_record)
    
    # Create DataFrame
    df = pd.DataFrame(all_fires)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved {len(all_fires)} total fires to {output_file}")
    print(f"\nBreakdown by region:")
    print(df.groupby('region').size())
    
    return df

if __name__ == '__main__':
    # Define regions matching frontend
    regions = {
        'california': {'lat': 37, 'lon': -120, 'radius_km': 500},
        'amazon': {'lat': -5, 'lon': -62, 'radius_km': 1500},
        'northamerica': {'lat': 45, 'lon': -100, 'radius_km': 2500},
        'southamerica': {'lat': -15, 'lon': -60, 'radius_km': 2500},
        'australia': {'lat': -25, 'lon': 135, 'radius_km': 2000},
        'canada': {'lat': 60, 'lon': -110, 'radius_km': 2000},
    }
    
    # Generate CSV for last 2 years with stricter thresholds for real fires only
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)  # Last 2 years
    
    print(f"\n🔥 GENERATING FIRE HISTORY CSV")
    print(f"📅 Time range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"🎯 Using HIGH FRP thresholds to filter out false positives (sunlight/reflections)")
    print(f"   - Small regions (CA, Amazon): FRP > 100 MW")
    print(f"   - Large regions (Americas): FRP > 1000 MW")
    
    df = generate_fire_history_csv(
        regions=regions,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        output_file='/app/data/fire_history.csv'
    )
    
    print("\n📊 Sample data:")
    print(df.head(10))
