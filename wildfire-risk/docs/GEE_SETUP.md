# Google Earth Engine Integration Setup

This guide helps you set up the Google Earth Engine (GEE) data pipeline for real-time satellite and environmental data.

## Prerequisites

1. **Google Earth Engine Account**
   - Sign up at: https://earthengine.google.com/signup/
   - It may take 1-2 days for approval

2. **Google Cloud Project** (for production)
   - Create a project at: https://console.cloud.google.com/
   - Enable Earth Engine API

## Setup Options

### Option 1: Development (User Authentication)

```bash
# Install Earth Engine package
pip install earthengine-api

# Authenticate (opens browser)
earthengine authenticate

# This creates credentials in:
# Windows: %USERPROFILE%\.config\earthengine\credentials
# Linux/Mac: ~/.config/earthengine/credentials
```

### Option 2: Production (Service Account)

1. **Create Service Account**
   ```bash
   # In Google Cloud Console
   # IAM & Admin > Service Accounts > Create Service Account
   # Name: wildfire-gee-service
   # Role: Earth Engine Resource Writer
   ```

2. **Generate Key**
   ```bash
   # Create and download JSON key
   # Save as: backend/gee-service-account.json
   ```

3. **Register Service Account with Earth Engine**
   ```bash
   # Go to: https://code.earthengine.google.com/
   # Click Assets tab
   # Add service account email to your assets permissions
   ```

4. **Update Docker Compose**
   ```yaml
   backend:
     environment:
       - GEE_SERVICE_ACCOUNT=/app/gee-service-account.json
     volumes:
       - ./backend/gee-service-account.json:/app/gee-service-account.json:ro
   ```

## Testing the Pipeline

### 1. Test GEE Connection

```bash
cd etl
python gee_connector.py
```

Expected output:
```json
{
  "location": {
    "latitude": 35.25,
    "longitude": -120.25,
    "buffer_km": 50
  },
  "weather": {
    "temperature_max": 25.3,
    "humidity_min": 42.1,
    "wind_speed": 4.2,
    "precipitation": 0.5
  },
  "vegetation": {
    "ndvi": 0.45,
    "evi": 0.38
  },
  "terrain": {
    "elevation": 342.5,
    "slope": 12.3,
    "aspect": 145.2
  }
}
```

### 2. Test API Endpoint

```bash
# Start backend
docker-compose up backend

# Test health check
curl http://localhost:8000/api/gee/health

# Fetch data for California
curl -X POST http://localhost:8000/api/gee/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 35.25,
    "longitude": -120.25,
    "buffer_km": 50,
    "days_back": 30
  }'
```

## Data Sources

The pipeline fetches data from multiple GEE datasets:

### 1. Weather Data (GRIDMET)
- **Dataset**: `IDAHO_EPSCOR/GRIDMET`
- **Resolution**: 4km
- **Variables**:
  - `tmmx`: Maximum temperature (°C)
  - `rmin`: Minimum relative humidity (%)
  - `vs`: Wind speed (m/s)
  - `pr`: Precipitation (mm)

### 2. Vegetation (Sentinel-2)
- **Dataset**: `COPERNICUS/S2_SR_HARMONIZED`
- **Resolution**: 10m
- **Indices**:
  - NDVI: Normalized Difference Vegetation Index
  - EVI: Enhanced Vegetation Index

### 3. Terrain (SRTM)
- **Dataset**: `USGS/SRTMGL1_003`
- **Resolution**: 30m
- **Variables**:
  - Elevation (m)
  - Slope (degrees)
  - Aspect (degrees)

### 4. Fire History (MODIS)
- **Dataset**: `MODIS/006/MOD14A1`
- **Resolution**: 1km
- **Variables**:
  - Fire detection count
  - Maximum fire radiative power

## Integration with Frontend

### Update API Client

```typescript
// frontend/src/api/client.ts

export async function fetchGEEData(
  lat: number,
  lon: number,
  bufferKm: number = 50,
  daysBack: number = 30
) {
  const response = await fetch(`${API_BASE}/gee/fetch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      latitude: lat,
      longitude: lon,
      buffer_km: bufferKm,
      days_back: daysBack
    })
  });
  return response.json();
}
```

### Add to State Store

```typescript
// frontend/src/state/store.ts

interface GEEData {
  weather: {
    temperature_max: number;
    humidity_min: number;
    wind_speed: number;
    precipitation: number;
  };
  vegetation: {
    ndvi: number;
    evi: number;
  };
  terrain: {
    elevation: number;
    slope: number;
  };
}

// Add to store
geeData: GEEData | null;
loadGEEData: async (lat: number, lon: number) => {
  const data = await fetchGEEData(lat, lon);
  set({ geeData: data });
}
```

## Troubleshooting

### Error: "EE service not initialized"
```bash
# Re-authenticate
earthengine authenticate

# Or check service account file exists
ls backend/gee-service-account.json
```

### Error: "Quota exceeded"
```
# GEE has usage quotas
# Free tier: 10,000 requests/day
# Check usage: https://code.earthengine.google.com/
```

### Error: "Cloud API not enabled"
```bash
# Enable Earth Engine API in GCP
gcloud services enable earthengine.googleapis.com
```

## Performance Tips

1. **Cache Results**: GEE queries can be slow (5-30 seconds)
   - Cache results in Redis/database
   - Update every 6-24 hours

2. **Use Smaller Regions**: 
   - Reduce buffer_km for faster queries
   - 10-50km is usually sufficient

3. **Batch Requests**:
   - Fetch data for multiple locations in parallel
   - Use async processing

## Production Deployment

```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - GEE_SERVICE_ACCOUNT=/app/gee-service-account.json
      - GEE_PROJECT_ID=your-gcp-project
    volumes:
      - ./secrets/gee-service-account.json:/app/gee-service-account.json:ro
```

## Next Steps

1. ✅ Set up GEE authentication
2. ✅ Test data pipeline
3. ✅ Integrate with backend API
4. 🔄 Add caching layer
5. 🔄 Create frontend UI components
6. 🔄 Add real-time updates
7. 🔄 Deploy to production

## Resources

- [GEE Python API Docs](https://developers.google.com/earth-engine/guides/python_install)
- [GEE Data Catalog](https://developers.google.com/earth-engine/datasets)
- [GEE Code Editor](https://code.earthengine.google.com/)
- [Sentinel-2 Data](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
