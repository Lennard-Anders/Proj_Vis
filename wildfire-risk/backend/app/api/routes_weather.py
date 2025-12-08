"""Weather heatmap API routes using Google Earth Engine."""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from ..services.weather import weather_service

router = APIRouter(prefix="/weather", tags=["weather"])


class WeatherHeatmapRequest(BaseModel):
    """Request for weather heatmap data."""
    date: str
    region: Optional[str] = None
    bbox: Optional[Dict[str, float]] = None


class WindPoint(BaseModel):
    """Wind data point."""
    latitude: float
    longitude: float
    wind_speed: float


class HumidityPoint(BaseModel):
    """Humidity data point."""
    latitude: float
    longitude: float
    humidity: float


class RainPoint(BaseModel):
    """Rain/precipitation data point."""
    latitude: float
    longitude: float
    rain: float


class WindHeatmapResponse(BaseModel):
    """Response with wind heatmap data."""
    data: List[WindPoint]
    date: str
    count: int


class HumidityHeatmapResponse(BaseModel):
    """Response with humidity heatmap data."""
    data: List[HumidityPoint]
    date: str
    count: int


class RainHeatmapResponse(BaseModel):
    """Response with rain heatmap data."""
    data: List[RainPoint]
    date: str
    count: int


@router.post("/wind/heatmap", response_model=WindHeatmapResponse)
async def get_wind_heatmap(request: WeatherHeatmapRequest):
    """
    Get wind speed heatmap data for a specific date using GEE.
    
    Query parameters:
    - date: Date in YYYY-MM-DD format
    - region: Optional region filter
    - bbox: Optional bounding box {min_lat, max_lat, min_lon, max_lon}
    """
    try:
        data = weather_service.get_wind_heatmap(
            date_str=request.date,
            region=request.region,
            bbox=request.bbox
        )
        
        return WindHeatmapResponse(
            data=data,
            date=request.date,
            count=len(data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wind data: {str(e)}")


@router.post("/humidity/heatmap", response_model=HumidityHeatmapResponse)
async def get_humidity_heatmap(request: WeatherHeatmapRequest):
    """
    Get relative humidity heatmap data for a specific date using GEE.
    
    Query parameters:
    - date: Date in YYYY-MM-DD format
    - region: Optional region filter
    - bbox: Optional bounding box {min_lat, max_lat, min_lon, max_lon}
    """
    try:
        data = weather_service.get_humidity_heatmap(
            date_str=request.date,
            region=request.region,
            bbox=request.bbox
        )
        
        return HumidityHeatmapResponse(
            data=data,
            date=request.date,
            count=len(data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching humidity data: {str(e)}")


@router.post("/rain/heatmap", response_model=RainHeatmapResponse)
async def get_rain_heatmap(request: WeatherHeatmapRequest):
    """
    Get precipitation heatmap data for a specific date using GEE.
    
    Query parameters:
    - date: Date in YYYY-MM-DD format
    - region: Optional region filter
    - bbox: Optional bounding box {min_lat, max_lat, min_lon, max_lon}
    """
    try:
        data = weather_service.get_rain_heatmap(
            date_str=request.date,
            region=request.region,
            bbox=request.bbox
        )
        
        return RainHeatmapResponse(
            data=data,
            date=request.date,
            count=len(data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rain data: {str(e)}")
