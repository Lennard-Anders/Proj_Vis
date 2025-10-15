# Data Directory

This directory is a placeholder for data files used in the Wildfire Risk Modeling system.

## Structure

```
data/
├── raw/                    # Raw ingested data (FDCF, weather)
├── processed/              # Processed and labeled data
├── features/               # Feature-engineered Parquet tiles
└── schema/                 # Data schemas and contracts
    ├── features_parquet_columns.json
    └── training_ranges.json
```

## Data Sources

### FDCF (Fire Detection and Characterization)
- Source: NOAA/NASA FIRMS VIIRS
- Access: Earth Engine or direct S3

### Weather Data
- Source: ERA5 Reanalysis, Open-Meteo, NWS
- Variables: t2m, dewpoint, u10, v10, gust, precipitation
- Resolution: 0.25° spatial, hourly temporal

### Climatology
- Source: PRISM, WorldClim
- Period: 1991-2020 baseline

## Getting Real Data

To populate this directory with actual data:

1. **Configure ETL**: Edit `etl/config.yaml` with your data sources and credentials
2. **Run Ingestion**: `cd etl && python ee_fdcf_ingest.py`
3. **Build Features**: `make etl`

## Data Contract

See `ml/data_contract.md` for detailed schema specifications.

## Attribution

Data sources used in this project:
- **NOAA VIIRS Active Fires**: Public domain
- **ERA5 Reanalysis**: Copernicus Climate Change Service (C3S)
- **PRISM Climatology**: Oregon State University

Please cite appropriately when using this system.
