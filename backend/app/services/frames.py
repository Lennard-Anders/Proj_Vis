"""
FDCF frame fetcher service
"""
from typing import Optional

from app.models.schemas import FramesResponse


class FramesService:
    """Service for fetching FDCF frame metadata"""
    
    def get_by_event_id(self, event_id: str) -> FramesResponse:
        """
        Get FDCF frames for a specific event.
        
        TODO: Connect to actual FDCF data source (Earth Engine, S3, etc.)
        """
        # Stub: return mock frame URIs
        times = [
            "2024-01-15T12:00:00Z",
            "2024-01-15T12:15:00Z",
            "2024-01-15T12:30:00Z",
            "2024-01-15T12:45:00Z",
        ]
        
        tiles = [
            f"s3://fdcf-bucket/event_{event_id}/frame_{i:04d}.tif"
            for i in range(len(times))
        ]
        
        return FramesResponse(times=times, tiles=tiles)
    
    def get_by_location(
        self,
        lat: float,
        lon: float,
        date: str
    ) -> FramesResponse:
        """
        Get FDCF frames for a specific location and date.
        
        TODO: Query FDCF database by spatial/temporal index
        """
        # Stub: return mock frames
        times = [
            f"{date}T12:00:00Z",
            f"{date}T13:00:00Z",
            f"{date}T14:00:00Z",
        ]
        
        tiles = [
            f"s3://fdcf-bucket/tile_h{int(lat*10):03d}v{int(lon*10):03d}/{date}/frame_{i:04d}.tif"
            for i in range(len(times))
        ]
        
        return FramesResponse(times=times, tiles=tiles)
