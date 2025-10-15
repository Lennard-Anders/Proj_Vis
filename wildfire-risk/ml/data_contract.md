# Wildfire Risk Feature Contract

All features are provided at daily cadence on a 0.25° grid. Records are keyed by `date` (YYYY-MM-DD), `lat`, and `lon`.

| Column | Type | Description | Units |
| ------ | ---- | ----------- | ----- |
| date | string | Observation date | YYYY-MM-DD |
| lat | float | Latitude | degrees |
| lon | float | Longitude | degrees |
| wind_speed_10m | float | Mean 10m wind speed | m/s |
| wind_dir_sin | float | Sine of wind direction | unitless |
| wind_dir_cos | float | Cosine of wind direction | unitless |
| gust_10m | float | 10m gust speed | m/s |
| t2m | float | 2m air temperature | Kelvin |
| dewpoint | float | Dew point temperature | Kelvin |
| rh | float | Relative humidity | % |
| vpd | float | Vapor pressure deficit | kPa |
| rain_24h | float | Accumulated precipitation (24h) | mm |
| rain_72h | float | Accumulated precipitation (72h) | mm |
| recent_fires_72h_20km | float | Detected fires within 20km over past 72h | count |
| ignition | int | Ignition label | 0/1 |
| dqf_mask | int | Data quality flag | mask |
| data_availability | float | Upstream data availability | fraction |
