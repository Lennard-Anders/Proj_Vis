"""Extract temperature data from historical dataset to create temperature_current.csv"""
import pandas as pd
from pathlib import Path

# Paths
data_dir = Path(__file__).parent.parent / 'data'
datasets_dir = data_dir / 'Datasets'
input_file = datasets_dir / 'df_america_cleaned.csv'
output_file = data_dir / 'temperature_current.csv'

# Load data
print(f"Loading data from {input_file}")
df = pd.read_csv(input_file)
df['dt'] = pd.to_datetime(df['dt'])

# Get latest date
latest_date = df['dt'].max()
print(f"Latest date in dataset: {latest_date}")

# Filter to latest data
latest = df[df['dt'] == latest_date].copy()

# Parse coordinates - handle different formats
def parse_lat(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.endswith('N'):
        return float(s[:-1])
    elif s.endswith('S'):
        return -float(s[:-1])
    elif s.endswith('-'):
        return -float(s[:-1])
    else:
        return float(s)

def parse_lon(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.endswith('W'):
        return -float(s[:-1])
    elif s.endswith('E'):
        return float(s[:-1])
    elif s.endswith('-'):
        return -float(s[:-1])
    else:
        return float(s)

latest['lat'] = latest['Latitude'].apply(parse_lat)
latest['lon'] = latest['Longitude'].apply(parse_lon)

# Create output dataframe
temp_df = latest[['lat', 'lon', 'AverageTemperature']].dropna()
temp_df.columns = ['latitude', 'longitude', 'temperature']

# Save
temp_df.to_csv(output_file, index=False)
print(f"✓ Created {output_file} with {len(temp_df)} temperature points")
print(f"  Lat range: {temp_df['latitude'].min():.2f} to {temp_df['latitude'].max():.2f}")
print(f"  Lon range: {temp_df['longitude'].min():.2f} to {temp_df['longitude'].max():.2f}")
print(f"  Temp range: {temp_df['temperature'].min():.2f}°C to {temp_df['temperature'].max():.2f}°C")
