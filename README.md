# Wildfire Risk Visualization Tool

A comprehensive web application for visualizing and analyzing wildfire risk across North America using real-time weather data, historical fire events, and predictive analytics.

## Overview

This tool provides interactive visualization of wildfire risk by combining:
- Historical wildfire event data (2023-2024) - 447 fire events
- Real-time weather conditions (temperature, humidity, wind, precipitation)
- AI-powered risk prediction models
- Interactive maps and data exploration tools

## Features

- **Interactive Risk Map**: Visualize wildfire risk with weather overlay layers
- **Fire History Analysis**: Explore historical wildfire events by region and time period
- **Monthly Distribution**: View fire event patterns across seasons
- **Weather Layer Toggle**: Switch between temperature, humidity, wind, and precipitation
- **What-If Analysis**: Click on the map to get AI-powered risk predictions for specific locations
- **Region Filtering**: Focus on specific areas (California, Southwest, Pacific Northwest, etc.)

## Prerequisites

Before installation, ensure you have the following installed:

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository

### Verify Prerequisites

```bash
docker --version
docker-compose --version
git --version
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Lennard-Anders/Proj_Vis.git
cd Proj_Vis/wildfire-risk
```

### 2. Verify Data Files

Ensure the following data files are present in the `data/` directory:

```
data/
├── fire_history.csv
├── humidity_current.csv
├── rain_current.csv
├── wind_current.csv
├── temperature_current.csv
├── weather_metadata.csv
└── Datasets/
    ├── predicted_fire_events_2023_2024.csv
    ├── weather_historical_2023_2024.csv
    └── df_america_cleaned.csv
```

All required data files are included in the repository.

## Running the Application

### Quick Start

From the `wildfire-risk` directory, run:

```bash
docker-compose up -d --build
```

This command will:
1. Build all Docker images (frontend, backend, nginx)
2. Start 7 containers:
   - **backend**: FastAPI application (port 8000)
   - **frontend**: React/Vite development server
   - **db**: PostgreSQL database (port 5432)
   - **nginx**: Reverse proxy (port 8080)
   - **prometheus**: Metrics collection (port 9090)
   - **grafana**: Monitoring dashboards (port 3000)
   - **nginx-exporter**: Nginx metrics exporter
3. Initialize the database with fire event data
4. Make the application available at **http://localhost:8080**

### Wait for Services to Start

The initial build and startup takes approximately 2-3 minutes. You can monitor the progress:

```bash
docker-compose logs -f
```

Press `Ctrl+C` to stop following the logs.

### Verify Services

Check that all containers are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                             STATUS              PORTS
wildfire-risk-backend-1          Up                  0.0.0.0:8000->8000/tcp
wildfire-risk-db-1               Up (healthy)        0.0.0.0:5432->5432/tcp
wildfire-risk-frontend-1         Up                  
wildfire-risk-grafana-1          Up                  0.0.0.0:3000->3000/tcp
wildfire-risk-nginx-1            Up                  0.0.0.0:8080->80/tcp
wildfire-risk-prometheus-1       Up                  0.0.0.0:9090->9090/tcp
wildfire-risk-nginx-exporter-1   Up                  0.0.0.0:9113->9113/tcp
```

### Access the Application

Open your web browser and navigate to:

**http://localhost:8080**

The application should load within 3-5 seconds.

### Stopping the Application

To stop all services:

```bash
docker-compose down
```

To stop and remove all data (including database):

```bash
docker-compose down -v
```

### Restarting Services

To restart a specific service (e.g., after code changes):

```bash
docker-compose restart backend
docker-compose restart frontend
```

## Using the Tool

### Main Interface

The application consists of three main panels:

#### 1. What-If Analysis (Left Panel)
**Purpose**: Analyze wildfire risk at specific locations

**How to Use**:
1. Click on any location on the center map
2. View AI-generated risk prediction percentage
3. See contributing weather factors:
   - Temperature impact
   - Humidity levels
   - Wind speed effects
   - Precipitation data
4. Explore risk breakdown and recommendations

**Features**:
- Real-time risk calculation
- Weather parameter breakdown
- Historical context comparison
- Risk level indicator (Low/Medium/High)

#### 2. Wildfire Risk Visualization (Center Panel)
**Purpose**: View weather conditions and fire risk across North America

**How to Use**:
1. **Toggle Weather Layers**:
   - Click 🌡️ **SHOW TEMP** - Display temperature heatmap
   - Click 💨 **SHOW WIND** - Show wind speed visualization
   - Click 💧 **SHOW HUMIDITY** - Display relative humidity levels
   - Click 🌧️ **SHOW RAIN** - Show precipitation data
   - Multiple layers can be active simultaneously

2. **Select Date**: 
   - Use date picker to view historical weather conditions
   - Default shows most recent available data

3. **Interact with Map**:
   - Click anywhere to get risk prediction
   - Zoom with mouse wheel or pinch gesture
   - Pan by clicking and dragging

**Color Coding**:
- **Temperature**: Blue (cold) → Yellow → Red (hot)
- **Wind**: Light blue (calm) → Dark blue (high winds)
- **Humidity**: Yellow (dry) → Blue (humid)
- **Rain**: White (no rain) → Blue (precipitation)

#### 3. Fire History (Right Panel)
**Purpose**: Explore historical wildfire events

**Components**:

1. **Global Context Map**:
   - Red dots indicate fire event locations
   - Dot size represents fire intensity
   - Interactive: click to focus on region

2. **Region Selector**:
   - Dropdown menu with predefined regions:
     - California 
     - Southwest 
     - Pacific Northwest 
     - Americas 
   - Numbers show event count per region
   - Updates map and charts when changed

3. **Year Selector**:
   - Filter events by year (2023 or 2024)
   - Shows total events for selected year
   - Automatically updates visualizations

4. **Fire History Distribution Chart**:
   - Bar chart showing monthly fire event counts
   - **Hover**: View detailed statistics
     - Average FRP (Fire Radiative Power)
     - Average confidence level
     - Average temperature
   - **Click bars**: Filter events to specific month
   - **Color coding**: 
     - Green: Low intensity (0-33%)
     - Yellow: Medium intensity (34-66%)
     - Red: High intensity (67-100%)

5. **Timeline View**:
   - Interactive timeline showing events by month
   - Fire icons represent individual events
   - **Hover**: See event summary
   - **Click**: View detailed event information
   - Horizontal scroll to explore time periods

### Key Interactions

| Action | Result |
|--------|--------|
| Click on map | Get AI risk prediction for that location |
| Click fire icon on timeline | View detailed fire event information |
| Click chart bar | Filter events to selected month |
| Toggle weather layer button | Show/hide weather parameter visualization |
| Select region from dropdown | Focus on specific geographic area |
| Select year | Filter events to chosen year |
| Hover over chart bar | View month statistics |

### Example Workflow

1. **Explore Fire History**:
   - Select "California" from region dropdown
   - Choose year "2024"
   - Observe monthly distribution in bar chart
   - Click on highest bar to see peak fire month

2. **Analyze Weather Conditions**:
   - Click "SHOW TEMP" to see temperature
   - Click "SHOW HUMIDITY" to overlay humidity
   - Observe correlation between hot/dry areas and fire events

3. **Get Risk Prediction**:
   - Click on a location in California
   - Review risk percentage in left panel
   - Check contributing factors (temperature, humidity, wind)
   - Note recommendations

## Project Structure

```
wildfire-risk/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── api/         # API route handlers
│   │   │   ├── routes_fire_history.py
│   │   │   ├── routes_weather.py
│   │   │   ├── routes_temperature.py
│   │   │   └── routes_ai_risk.py
│   │   ├── services/    # Business logic
│   │   │   ├── weather.py
│   │   │   ├── temperature.py
│   │   │   └── fire_history.py
│   │   ├── models/      # Data models
│   │   ├── core/        # Configuration
│   │   └── main.py      # Application entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React/Vite frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   │   ├── TriView/      # Main map visualization
│   │   │   ├── FireHistoryHistogram/
│   │   │   ├── EventExplorer/
│   │   │   └── WorldMap/
│   │   ├── api/         # API client functions
│   │   ├── state/       # Zustand state management
│   │   └── App.tsx      # Main application
│   ├── package.json
│   └── vite.config.ts
├── data/               # Data files
│   ├── fire_history.csv
│   ├── temperature_current.csv
│   ├── humidity_current.csv
│   ├── wind_current.csv
│   ├── rain_current.csv
│   ├── weather_metadata.csv
│   └── Datasets/
│       ├── predicted_fire_events_2023_2024.csv
│       └── weather_historical_2023_2024.csv
├── etl/               # Data processing scripts
│   ├── fetch_weather_data.py
│   ├── generate_fire_risk_from_weather.py
│   ├── extract_temperature_data.py
│   └── requirements.txt
├── infra/            # Infrastructure configuration
│   ├── k8s/         # Kubernetes manifests
│   ├── nginx/       # Nginx configuration
│   ├── prometheus/  # Monitoring config
│   └── grafana/     # Dashboards
├── docker-compose.yml
└── README.md
```

## Data Sources

### Fire Event Data
- **File**: `data/Datasets/predicted_fire_events_2023_2024.csv`
- **Source**: From weather conditions using temperature thresholds and risk scoring
- **Coverage**: North America (26.9°N - 49.0°N, -123.5°W to -69.2°W)
- **Period**: 2023-2024
- **Records**: 447 fire events
- **Attributes**:
  - Latitude/Longitude coordinates
  - Date and time
  - Fire Radiative Power (FRP)
  - Brightness temperature
  - Burned area (km²)
  - Confidence level
  - Risk score
  - Weather conditions (temperature, wind, humidity)

### Weather Data
- **Source**: GRIDMET dataset via Google Earth Engine
- **Parameters**:
  - **Temperature**: Max daily temperature (°C)
  - **Humidity**: Minimum relative humidity (%)
  - **Wind Speed**: Wind velocity at 10m (m/s)
  - **Precipitation**: Daily precipitation (mm)
- **Coverage**: North America (GRIDMET dataset bounds)
- **Resolution**: 2-degree grid spacing
- **Data Points**: 212-437 points per parameter
- **Files**:
  - `temperature_current.csv` - 437 temperature points
  - `humidity_current.csv` - 212 humidity measurements
  - `wind_current.csv` - 212 wind speed values
  - `rain_current.csv` - 212 precipitation amounts

### Historical Temperature Data
- **File**: `data/Datasets/df_america_cleaned.csv`
- **Source**: Global historical temperature records
- **Coverage**: Americas region
- **Used For**: Temperature baseline comparisons and historical context

## Technology Stack

### Frontend
- **React 18**: Modern UI framework with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Deck.gl**: WebGL-powered geospatial visualization
- **Zustand**: Lightweight state management
- **Mapbox**: Base map tiles

### Backend
- **Python 3.11**: Modern Python runtime
- **FastAPI**: High-performance async web framework
- **Pandas**: Data manipulation and analysis
- **PostgreSQL 15**: Relational database
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for database operations

### Infrastructure
- **Docker**: Application containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx 1.27**: Reverse proxy and static file server
- **Prometheus**: Metrics collection and storage
- **Grafana**: Monitoring dashboards and visualization

### Data Processing
- **Google Earth Engine**: Satellite data access (GRIDMET)
- **NumPy**: Numerical computations
- **GeoPandas**: Geospatial data processing

## API Endpoints

The backend exposes a RESTful API documented with OpenAPI/Swagger.

### Fire History
- `GET /api/fire-history/events` - Get fire events with filtering
  - Query params: region, year, start_date, end_date
- `GET /api/fire-history/regions` - Get available region definitions
- `GET /api/fire-history/stats` - Get statistical summaries

### Weather Data
- `POST /api/weather/wind/heatmap` - Get wind speed heatmap data
  - Body: {date, region, bbox}
- `POST /api/weather/humidity/heatmap` - Get humidity heatmap data
- `POST /api/weather/rain/heatmap` - Get precipitation heatmap data

### Temperature Data
- `POST /api/temperature/heatmap` - Get temperature heatmap data
  - Body: {date, region, bbox}
- `GET /api/temperature/stats` - Get historical temperature statistics

### Risk Analysis
- `POST /api/ai-risk/predict` - Get AI-powered risk prediction
  - Body: {latitude, longitude, temperature, humidity, wind, rainfall}
- `GET /api/risk/scenario` - Get scenario-based risk assessment

**Full API Documentation**: http://localhost:8000/docs (when backend is running)

## Troubleshooting

### Port Already in Use

**Error**: `Bind for 0.0.0.0:8080 failed: port is already allocated`

**Solution**: Change the nginx port in `docker-compose.yml`:

```yaml
nginx:
  ports:
    - "8081:80"  # Change 8080 to 8081
```

Then access the application at http://localhost:8081

### Database Connection Issues

**Error**: Backend logs show database connection errors

**Solution**: Reset the database:

```bash
docker-compose down -v
docker-compose up -d
```

Wait 30 seconds for the database to initialize, then check:

```bash
docker-compose logs db
```

### Frontend Not Loading

**Issue**: Blank page or "Loading..." message persists

**Solutions**:
1. **Clear browser cache**: 
   - Chrome/Firefox: Ctrl + Shift + R (Windows) / Cmd + Shift + R (Mac)
   - Edge: Ctrl + F5

2. **Check frontend logs**:
   ```bash
   docker-compose logs frontend
   ```

3. **Rebuild frontend**:
   ```bash
   docker-compose down
   docker-compose up -d --build frontend
   ```

### Backend Errors

**Issue**: API calls failing or returning errors

**Check backend logs**:

```bash
docker-compose logs backend
```

**Common issues**:
- Missing data files: Verify files in `data/` directory
- Database not ready: Wait for `db` container to be healthy
- Port conflicts: Check if port 8000 is available

### No Data Showing on Maps

**Issue**: Weather layers or fire events not displaying

**Verify data files are mounted**:

```bash
docker exec wildfire-risk-backend-1 ls -la /app/data
```

Expected output should show all CSV files.

**Check file permissions**:
```bash
docker exec wildfire-risk-backend-1 cat /app/data/temperature_current.csv | head -5
```


