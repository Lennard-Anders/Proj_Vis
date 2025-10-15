"""
Risk assessment endpoints
"""
from typing import Optional
from fastapi import APIRouter, Query, Depends
import numpy as np

from app.models.schemas import RiskResponse, RiskTile, QualityData, BBox
from app.services.risk import RiskService
from app.deps import get_model_registry

router = APIRouter()


@router.get("", response_model=RiskResponse)
async def get_risk(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    bbox: Optional[str] = Query(None, description="Bounding box as minLon,minLat,maxLon,maxLat"),
    registry = Depends(get_model_registry)
):
    """
    Get risk assessment for a given date and bounding box.
    Returns a grid of 0.25° tiles with probabilities and confidence intervals.
    
    TODO: Replace with actual model inference on real data
    """
    # Parse bbox
    if bbox:
        coords = [float(x) for x in bbox.split(",")]
        bbox_obj = BBox(
            min_lon=coords[0],
            min_lat=coords[1],
            max_lon=coords[2],
            max_lat=coords[3]
        )
    else:
        # Default to a small region in California
        bbox_obj = BBox(min_lon=-122.0, min_lat=37.0, max_lon=-121.0, max_lat=38.0)
    
    # Initialize risk service
    risk_service = RiskService(registry)
    
    # Generate risk grid
    grid = risk_service.compute_risk_grid(date, bbox_obj)
    
    # Generate quality data (stub)
    quality = QualityData(
        dqf_mask=[1] * len(grid),  # All good quality
        data_availability=[0.95] * len(grid)  # 95% data available
    )
    
    return RiskResponse(
        grid=grid,
        quality=quality,
        date=date,
        bbox=bbox_obj
    )
