from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()


class Frame(BaseModel):
    """A single frame in the wildfire spread simulation"""
    timestamp: datetime
    risk_map: List[List[float]]
    spread_intensity: float
    affected_area_km2: float


class FramesRequest(BaseModel):
    """Request model for simulation frames"""
    start_latitude: float
    start_longitude: float
    end_latitude: float
    end_longitude: float
    start_time: datetime
    duration_hours: int
    interval_hours: int = 1


class FramesResponse(BaseModel):
    """Response model for simulation frames"""
    frames: List[Frame]
    total_frames: int
    spatial_resolution: float


@router.post("/", response_model=FramesResponse)
async def get_frames(request: FramesRequest):
    """
    Get temporal frames for wildfire spread visualization
    """
    try:
        num_frames = request.duration_hours // request.interval_hours
        
        # Generate placeholder frames
        frames = []
        for i in range(num_frames):
            # Simple 5x5 grid placeholder
            risk_map = [
                [0.1 + (i * 0.05) for _ in range(5)]
                for _ in range(5)
            ]
            
            frame = Frame(
                timestamp=request.start_time,
                risk_map=risk_map,
                spread_intensity=0.3 + (i * 0.1),
                affected_area_km2=100.0 + (i * 50.0)
            )
            frames.append(frame)
        
        return FramesResponse(
            frames=frames,
            total_frames=len(frames),
            spatial_resolution=0.25  # 0.25 degree resolution
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest")
async def get_latest_frame(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude")
):
    """
    Get the latest frame for a specific location
    """
    try:
        # Placeholder for latest frame
        return {
            "timestamp": datetime.now().isoformat(),
            "risk_score": 0.45,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
