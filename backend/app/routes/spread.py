from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
from datetime import datetime

router = APIRouter()


class SpreadRequest(BaseModel):
    """Request model for spread prediction"""
    ignition_latitude: float
    ignition_longitude: float
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float  # degrees
    fuel_type: str
    simulation_hours: int = 24


class SpreadPoint(BaseModel):
    """A point in the spread prediction"""
    latitude: float
    longitude: float
    risk_score: float
    arrival_time_hours: float


class SpreadResponse(BaseModel):
    """Response model for spread prediction"""
    ignition_point: Tuple[float, float]
    spread_points: List[SpreadPoint]
    total_area_km2: float
    max_distance_km: float
    simulation_time: datetime


@router.post("/", response_model=SpreadResponse)
async def predict_spread(request: SpreadRequest):
    """
    Predict wildfire spread from ignition point
    Uses surrogate model for fast inference
    """
    try:
        # Simple radial spread simulation (placeholder)
        spread_points = []
        
        # Generate spread points in a pattern
        num_points = 20
        for i in range(num_points):
            angle = (i / num_points) * 360
            # Bias spread in wind direction
            if abs(angle - request.wind_direction) < 90:
                distance = 0.1 * (request.wind_speed / 10.0)
            else:
                distance = 0.05 * (request.wind_speed / 10.0)
            
            lat_offset = distance * (i / num_points)
            lon_offset = distance * (i / num_points)
            
            spread_points.append(
                SpreadPoint(
                    latitude=request.ignition_latitude + lat_offset,
                    longitude=request.ignition_longitude + lon_offset,
                    risk_score=0.8 - (i / num_points) * 0.3,
                    arrival_time_hours=i * (request.simulation_hours / num_points)
                )
            )
        
        return SpreadResponse(
            ignition_point=(request.ignition_latitude, request.ignition_longitude),
            spread_points=spread_points,
            total_area_km2=150.0,
            max_distance_km=5.5,
            simulation_time=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_spread_history():
    """
    Get historical spread patterns
    """
    return {
        "message": "Historical spread patterns endpoint",
        "total_events": 0,
        "events": []
    }
