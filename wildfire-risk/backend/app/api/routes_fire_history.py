"""
Google Earth Engine Fire History API
Fetches historical wildfire events with detailed information
"""
import ee
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import sys
from pathlib import Path
import pandas as pd
import os
import math

sys.path.append(str(Path(__file__).parent.parent.parent / 'etl'))
from gee_connector import GEEDataPipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gee", tags=["google-earth-engine"])

_gee_pipeline: Optional[GEEDataPipeline] = None
# Use predicted fire events from weather data (2023-2024)
FIRE_HISTORY_CSV = Path("/app/data/Datasets/predicted_fire_events_2023_2024.csv")
FORCE_CSV = os.getenv("FIRE_HISTORY_FORCE_CSV", "1") == "1"

def get_gee_pipeline() -> GEEDataPipeline:
    """Get or create GEE pipeline instance"""
    global _gee_pipeline
    if _gee_pipeline is None:
        try:
            _gee_pipeline = GEEDataPipeline()
        except Exception as e:
            logger.error(f"Failed to initialize GEE: {e}")
            raise HTTPException(
                status_code=503,
                detail="Google Earth Engine service unavailable."
            )
    return _gee_pipeline


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance between two lat/lon points in kilometers."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


class FireEvent(BaseModel):
    """Individual fire detection event"""
    event_id: str
    latitude: float
    longitude: float
    date: str
    fire_radiative_power: float
    confidence: int
    brightness_temp: float
    area_km2: Optional[float] = None


class FireHistoryResponse(BaseModel):
    """Response with fire history events"""
    events: List[FireEvent]
    total_events: int
    period_start: str
    period_end: str
    region_center: Dict[str, float]


@router.get("/fire-history", response_model=FireHistoryResponse)
async def get_fire_history(
    lat: float = Query(None, ge=-90, le=90, description="Center latitude (optional)"),
    lon: float = Query(None, ge=-180, le=180, description="Center longitude (optional)"),
    radius_km: float = Query(None, gt=0, le=5000, description="Search radius in km (optional)"),
    days_back: int = Query(None, gt=0, le=10950, description="Days to look back from today (optional)"),
    start_date: str = Query(None, description="Start date YYYY-MM-DD (optional)"),
    end_date: str = Query(None, description="End date YYYY-MM-DD (optional)")
):
    """
    Fetch historical wildfire events from MODIS satellite data
    
    If lat/lon not provided, searches entire North and South America
    Use either days_back OR start_date/end_date for time range
    
    Serves from cached CSV if available for faster response
    """
    try:
        # Try to load from cached CSV first for speed; optionally force CSV-only mode
        if FIRE_HISTORY_CSV.exists():
            logger.info(f"📂 Loading fire history from cached CSV: {FIRE_HISTORY_CSV}")
            try:
                df = pd.read_csv(FIRE_HISTORY_CSV)
                # Normalize date column
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date']).dt.date

                # Derive requested date window
                if start_date and end_date:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                else:
                    end_dt = datetime.utcnow().date()
                    start_dt = end_dt - timedelta(days=days_back or 1825)

                # Apply date filter
                df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]

                # Apply spatial filter if lat/lon provided
                if lat is not None and lon is not None:
                    radius = radius_km or 100.0
                    df = df[df.apply(lambda row: _haversine_km(lat, lon, row['latitude'], row['longitude']) <= radius, axis=1)]

                # Convert to response format
                events = []
                for _, row in df.iterrows():
                    events.append({
                        "event_id": str(row['event_id']),
                        "latitude": float(row['latitude']),
                        "longitude": float(row['longitude']),
                        "date": str(row['date']),
                        "fire_radiative_power": float(row['fire_radiative_power']),
                        "confidence": int(row['confidence']),
                        "brightness_temp": float(row.get('brightness_temp', 0.0)),
                        "area_km2": float(row.get('area_km2', 1.0))
                    })

                logger.info(f"✅ Loaded {len(events)} fires from CSV cache (filtered)")
                return FireHistoryResponse(
                    events=events,
                    total_events=len(events),
                    period_start=start_dt.isoformat(),
                    period_end=end_dt.isoformat(),
                    region_center={"latitude": lat or 0, "longitude": lon or 0}
                )
            except Exception as e:
                logger.warning(f"Failed to load CSV cache: {e}, falling back to GEE query")
        else:
            if FORCE_CSV:
                logger.error("Fire history CSV not found and GEE is disabled (FORCE_CSV=1)")
                raise HTTPException(status_code=503, detail="Fire history CSV not found; GEE disabled")
        
        # Fall back to GEE query if allowed
        logger.info("🌍 Querying Google Earth Engine for fire history")
        pipeline = get_gee_pipeline()
        
        # Create region of interest
        if lat is not None and lon is not None:
            # Point-based search
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer((radius_km or 100) * 1000)
        else:
            # Continental Americas search (North + South America)
            # Bounding box: roughly -170 to -30 longitude, -60 to 70 latitude
            region = ee.Geometry.Rectangle([-170, -60, -30, 70])
        
        # Calculate date range - support both days_back and explicit dates
        if start_date and end_date:
            # Use explicit date range
            query_start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            # Use days_back (default 5 years)
            query_end_date = datetime.now()
            query_start_date = query_end_date - timedelta(days=days_back or 1825)
        
        # Fetch MODIS fire data - use max composite for better fire detection
        composite = ee.ImageCollection('MODIS/061/MOD14A1') \
            .filterDate(query_start_date.strftime('%Y-%m-%d'), query_end_date.strftime('%Y-%m-%d')) \
            .filterBounds(region) \
            .select(['MaxFRP', 'QA']) \
            .max()  # Create composite to aggregate fires
        
        # Adjust threshold and sample size based on query type
        is_point_query = lat is not None and lon is not None
        if is_point_query:
            # Point-based query: lower threshold, more samples
            frp_threshold = 50
            max_samples = 2000
            scale = 1000  # 1km resolution
        else:
            # Continental query: higher threshold for major fires only, faster processing
            frp_threshold = 500  # Only very large fires for Americas-wide view
            max_samples = 200  # Fewer samples for speed
            scale = 5000  # 5km resolution for faster processing
        
        fire_mask = composite.select('MaxFRP').gt(frp_threshold)
        
        # Add land mask to filter out ocean false positives
        # Using MODIS land cover to ensure fires are on land
        land_mask = ee.Image('MODIS/006/MCD12Q1/2020_01_01').select('LC_Type1').neq(0)  # 0 = water
        
        masked_composite = composite.updateMask(fire_mask).updateMask(land_mask)
        
        # Sample fire pixels with geometries
        fire_samples = masked_composite.sample(
            region=region,
            scale=scale,  # Use dynamic scale based on query type
            numPixels=max_samples,
            seed=42,
            geometries=True
        )
        
        features_list = fire_samples.getInfo()
        
        # Convert to fire events
        events = []
        for idx, feature in enumerate(features_list.get('features', [])):
            props = feature['properties']
            geom = feature.get('geometry')
            
            if not geom or geom['type'] != 'Point':
                continue
                
            coords = geom['coordinates']
            lon, lat = coords[0], coords[1]
            
            # Calculate approximate area (1km pixel)
            area_km2 = 1.0  # MODIS pixel is ~1km²
            
            # Extract confidence from QA band
            qa = int(props.get('QA', 0))
            confidence_bits = (qa >> 7) & 3
            
            if confidence_bits == 0:
                confidence = 33
            elif confidence_bits == 1:
                confidence = 66
            else:
                confidence = 99
            
            if qa == 0 and props.get('MaxFRP', 0) > 0:
                confidence = 66
            
            # Use period midpoint as date estimate (composite doesn't have exact date)
            midpoint_date = query_start_date + (query_end_date - query_start_date) / 2
            
            events.append(FireEvent(
                event_id=f"fire_{query_start_date.year}_{idx}",
                latitude=lat,
                longitude=lon,
                date=midpoint_date.strftime('%Y-%m-%d'),
                fire_radiative_power=float(props.get('MaxFRP', 0)),
                confidence=confidence,
                brightness_temp=0.0,
                area_km2=area_km2
            ))
        
        # Set region center (use provided coords or Americas center)
        region_lat = lat if lat is not None else 0.0  # Center of Americas
        region_lon = lon if lon is not None else -100.0  # Center of Americas
        
        return FireHistoryResponse(
            events=events,
            total_events=len(events),
            period_start=query_start_date.strftime('%Y-%m-%d'),
            period_end=query_end_date.strftime('%Y-%m-%d'),
            region_center={'latitude': region_lat, 'longitude': region_lon}
        )
        
    except Exception as e:
        logger.error(f"Error fetching fire history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch fire history: {str(e)}")


@router.get("/fire-analysis/{event_id}")
async def get_fire_analysis(
    event_id: str,
    lat: float = Query(..., description="Fire event latitude"),
    lon: float = Query(..., description="Fire event longitude"),
    date: str = Query(..., description="Fire event date (YYYY-MM-DD)")
):
    """
    Get detailed analysis for a specific fire event
    
    Returns environmental conditions, terrain analysis, and fire characteristics
    """
    try:
        pipeline = get_gee_pipeline()
        
        # Fetch data for the fire location on the fire date
        point = ee.Geometry.Point([lon, lat])
        region = point.buffer(5000)  # 5km radius around fire
        
        # Parse date
        fire_date = datetime.strptime(date, '%Y-%m-%d')
        start_date = (fire_date - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = fire_date.strftime('%Y-%m-%d')
        
        # Get weather conditions
        weather = pipeline.get_weather_data(region, start_date, end_date) or {}
        
        # Get vegetation
        vegetation = pipeline.get_vegetation_indices(region, start_date, end_date) or {}
        
        # Get terrain
        terrain = pipeline.get_elevation_slope(region) or {}
        
        # Get fire intensity details
        fire_data = ee.ImageCollection('MODIS/061/MOD14A1') \
            .filterDate(start_date, end_date) \
            .filterBounds(region) \
            .select(['MaxFRP']) \
            .max() \
            .reduceRegion(
                reducer=ee.Reducer.max(),
                geometry=region,
                scale=1000
            ).getInfo()
        
        # Generate analysis description with safe null handling
        temp_k = weather.get('temperature_max', 273.15)
        temp_c = float((temp_k - 273.15) if temp_k is not None else 0.0)
        humidity = float(weather.get('humidity_min') or 0.0)
        wind = float(weather.get('wind_speed') or 0.0)
        slope_deg = float(terrain.get('slope') or 0.0)
        elevation_m = float(terrain.get('elevation') or 0.0)
        ndvi = float(vegetation.get('ndvi') or 0.0)
        
        # Determine fire risk factors
        risk_factors = []
        if temp_c > 30:
            risk_factors.append(f"High temperature ({temp_c:.1f}°C)")
        if humidity < 30:
            risk_factors.append(f"Low humidity ({humidity:.0f}%)")
        if wind > 5:
            risk_factors.append(f"Strong winds ({wind:.1f} m/s)")
        if slope_deg > 15:
            risk_factors.append(f"Steep terrain ({slope_deg:.1f}°)")
        if ndvi < 0.3:
            risk_factors.append(f"Dry vegetation (NDVI: {ndvi:.2f})")
        
        description = (
            f"Fire detected at {lat:.4f}°N, {lon:.4f}°E on {date}. "
            f"Location: {elevation_m:.0f}m elevation on {slope_deg:.1f}° slope. "
            f"Conditions: {temp_c:.1f}°C, {humidity:.0f}% humidity, {wind:.1f} m/s winds. "
        )
        
        if risk_factors:
            description += f"Contributing factors: {', '.join(risk_factors)}."
        
        return {
            'event_id': event_id,
            'location': {
                'latitude': lat,
                'longitude': lon,
                'elevation_m': elevation_m,
                'slope_degrees': slope_deg,
                'aspect_degrees': float(terrain.get('aspect') or 0.0)
            },
            'fire_data': {
                'date': date,
                'max_frp': float(fire_data.get('MaxFRP') or 0.0),
            },
            'environmental_conditions': {
                'temperature_c': temp_c,
                'humidity_percent': humidity,
                'wind_speed_ms': wind,
                'precipitation_mm': float(weather.get('precipitation') or 0.0),
                'ndvi': ndvi,
                'evi': float(vegetation.get('evi') or 0.0)
            },
            'risk_factors': risk_factors,
            'description': description,
            'analysis': {
                'severity': 'High' if float(fire_data.get('MaxFRP') or 0) > 100 else 'Medium' if float(fire_data.get('MaxFRP') or 0) > 50 else 'Low',
                'terrain_risk': 'High' if slope_deg > 20 else 'Medium' if slope_deg > 10 else 'Low',
                'weather_risk': 'High' if len(risk_factors) >= 3 else 'Medium' if len(risk_factors) >= 2 else 'Low'
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing fire event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze fire: {str(e)}")
