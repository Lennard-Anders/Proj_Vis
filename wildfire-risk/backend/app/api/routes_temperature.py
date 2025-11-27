"""Temperature API routes."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import date

from ..services.temperature import temperature_service

router = APIRouter(prefix="/temperature", tags=["temperature"])


class TemperatureHeatmapRequest(BaseModel):
    """Request for temperature heatmap data."""
    date: str
    region: Optional[str] = None
    bbox: Optional[Dict[str, float]] = None


class TemperaturePoint(BaseModel):
    """Temperature data point."""
    latitude: float
    longitude: float
    temperature: float
    uncertainty: float = 0.0
    city: str = ""
    country: str = ""


class TemperatureHeatmapResponse(BaseModel):
    """Response with temperature heatmap data."""
    data: List[TemperaturePoint]
    date: str
    count: int


class HistoricalStatsResponse(BaseModel):
    """Historical temperature statistics."""
    mean_temp: float
    max_temp: float
    min_temp: float
    std_temp: float
    data_points: int


@router.post("/heatmap", response_model=TemperatureHeatmapResponse)
async def get_temperature_heatmap(request: TemperatureHeatmapRequest):
    """
    Get temperature heatmap data for a specific date.
    
    Query parameters:
    - date: Date in YYYY-MM-DD format
    - region: Optional region filter (california, north_america, etc.)
    - bbox: Optional bounding box {min_lat, max_lat, min_lon, max_lon}
    """
    try:
        data = temperature_service.get_temperature_heatmap(
            date_str=request.date,
            region=request.region,
            bbox=request.bbox
        )
        
        return TemperatureHeatmapResponse(
            data=data,
            date=request.date,
            count=len(data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching temperature data: {str(e)}")


@router.get("/stats", response_model=HistoricalStatsResponse)
async def get_historical_stats(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(50, description="Search radius in kilometers")
):
    """
    Get historical temperature statistics for a location.
    
    Query parameters:
    - lat: Latitude
    - lon: Longitude
    - radius_km: Search radius in kilometers (default: 50)
    """
    try:
        stats = temperature_service.get_historical_stats(lat, lon, radius_km)
        return HistoricalStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical stats: {str(e)}")
