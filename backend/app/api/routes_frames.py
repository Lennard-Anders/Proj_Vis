"""
FDCF frame fetcher endpoints
"""
from typing import Optional
from fastapi import APIRouter, Query

from app.models.schemas import FramesResponse
from app.services.frames import FramesService

router = APIRouter()


@router.get("", response_model=FramesResponse)
async def get_frames(
    event_id: Optional[str] = Query(None, description="Event ID"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """
    Get FDCF frame metadata for a specific event or location.
    
    TODO: Connect to actual FDCF data source
    """
    frames_service = FramesService()
    
    if event_id:
        frames = frames_service.get_by_event_id(event_id)
    elif lat and lon and date:
        frames = frames_service.get_by_location(lat, lon, date)
    else:
        # Return empty response
        return FramesResponse(times=[], tiles=[])
    
    return frames
