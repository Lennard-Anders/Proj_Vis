"""
API routes for Google Earth Engine data
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
import logging
import sys
from pathlib import Path

# Add etl directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'etl'))

from gee_connector import GEEDataPipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gee", tags=["google-earth-engine"])

# Initialize GEE pipeline (lazy loading)
_gee_pipeline: Optional[GEEDataPipeline] = None


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
                detail="Google Earth Engine service unavailable. Please check credentials."
            )
    return _gee_pipeline


class GEEDataRequest(BaseModel):
    """Request model for GEE data"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    buffer_km: float = Field(50, gt=0, le=500, description="Buffer radius in km")
    days_back: int = Field(30, gt=0, le=365, description="Days to look back")


class GEEDataResponse(BaseModel):
    """Response model for GEE data"""
    location: dict
    period: dict
    weather: dict
    vegetation: dict
    terrain: dict
    fire_history: dict
    timestamp: str


@router.post("/fetch", response_model=GEEDataResponse)
async def fetch_gee_data(request: GEEDataRequest):
    """
    Fetch satellite and environmental data from Google Earth Engine
    
    Args:
        request: GEE data request parameters
        
    Returns:
        Complete dataset including weather, vegetation, terrain, and fire history
    """
    try:
        pipeline = get_gee_pipeline()
        
        data = pipeline.fetch_complete_dataset(
            latitude=request.latitude,
            longitude=request.longitude,
            buffer_km=request.buffer_km,
            days_back=request.days_back
        )
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching GEE data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather")
async def get_weather(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    days: int = Query(7, gt=0, le=90)
):
    """
    Get weather data for a location
    
    Args:
        lat: Latitude
        lon: Longitude  
        days: Days to look back
        
    Returns:
        Weather statistics
    """
    try:
        pipeline = get_gee_pipeline()
        
        from datetime import datetime, timedelta
        import ee
        
        point = ee.Geometry.Point([lon, lat])
        region = point.buffer(10000)  # 10km buffer
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        weather = pipeline.get_weather_data(
            region,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        return weather
        
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vegetation")
async def get_vegetation(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    days: int = Query(30, gt=0, le=90)
):
    """
    Get vegetation indices for a location
    
    Args:
        lat: Latitude
        lon: Longitude
        days: Days to look back
        
    Returns:
        Vegetation index statistics (NDVI, EVI)
    """
    try:
        pipeline = get_gee_pipeline()
        
        from datetime import datetime, timedelta
        import ee
        
        point = ee.Geometry.Point([lon, lat])
        region = point.buffer(10000)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        vegetation = pipeline.get_vegetation_indices(
            region,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        return vegetation
        
    except Exception as e:
        logger.error(f"Error fetching vegetation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Check if Google Earth Engine is accessible
    
    Returns:
        Health status
    """
    try:
        pipeline = get_gee_pipeline()
        return {
            "status": "healthy",
            "service": "Google Earth Engine",
            "message": "GEE connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Google Earth Engine",
            "error": str(e)
        }
