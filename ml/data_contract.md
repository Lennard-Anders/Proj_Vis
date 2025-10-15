# Data Contract for Parquet Feature Tiles

## Schema

### Keys
- `date`: Date (YYYY-MM-DD format, string)
- `lat`: Latitude (float, degrees)
- `lon`: Longitude (float, degrees)

### Static Features
- `month`: Month of year (integer, 1-12)
- `clim_mean`: Climatological mean temperature (float, Kelvin)
- `clim_amp`: Climatological amplitude (float, Kelvin)
- `region_id`: Region identifier (integer)

### Dynamic Weather Features
- `wind_speed_10m`: Wind speed at 10m (float, m/s)
- `wind_dir_sin`: Wind direction sine component (float, -1 to 1)
- `wind_dir_cos`: Wind direction cosine component (float, -1 to 1)
- `gust_10m`: Wind gust at 10m (float, m/s)
- `t2m`: Temperature at 2m (float, Kelvin)
- `dewpoint`: Dewpoint temperature (float, Kelvin)
- `rh`: Relative humidity (float, %, 0-100)
- `vpd`: Vapor pressure deficit (float, kPa)
- `rain_24h`: 24-hour cumulative precipitation (float, mm)
- `rain_72h`: 72-hour cumulative precipitation (float, mm)
- `recent_fires_72h_20km`: Recent fire count within 20km in last 72h (integer)

### Labels
- `ignition`: Fire ignition label (integer, 0 or 1)

### Quality
- `dqf_mask`: Data quality flag (integer)
  - 0: Missing data
  - 1: Good quality
  - 2: Suspicious values
  - 3: Out of range
- `data_availability`: Data availability score (float, 0-1)

## Units

All meteorological variables use SI units:
- Temperature: Kelvin (K)
- Wind speed: meters per second (m/s)
- Precipitation: millimeters (mm)
- Pressure: kilopascals (kPa)

## Spatial Resolution

- Grid resolution: 0.25° (~28 km at equator)
- Projection: WGS84 (EPSG:4326)

## Temporal Resolution

- Daily aggregates
- Lagged features computed from hourly/6-hourly data

## Missing Values

- Missing numeric values encoded as NaN
- Quality flags indicate data completeness

## Usage

Load with Pandas or Polars:

```python
import pandas as pd
df = pd.read_parquet('features_2024_01.parquet')
```

Query with DuckDB:

```sql
SELECT * FROM read_parquet('features_*.parquet')
WHERE date = '2024-01-15' AND lat BETWEEN 37 AND 38
```
