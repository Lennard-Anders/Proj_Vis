"""
Fire spread simulation endpoints
"""
from fastapi import APIRouter

from app.models.schemas import SpreadRequest, SpreadResponse, SpreadMetrics
from app.services.spread import SpreadService

router = APIRouter()


@router.post("/run", response_model=SpreadResponse)
async def run_spread_simulation(request: SpreadRequest):
    """
    Run wind-driven fire spread simulation.
    
    Uses an anisotropic growth model with 8-neighbor stencil.
    
    TODO: Enhance with fuel models and terrain effects
    """
    spread_service = SpreadService()
    
    result = spread_service.simulate_spread(
        lat=request.lat,
        lon=request.lon,
        wind_speed=request.wind_speed_10m,
        wind_dir=request.wind_dir,
        duration_hours=request.duration_hours,
        steps=request.steps
    )
    
    return SpreadResponse(
        footprint_geojson=result["footprint"],
        metrics=SpreadMetrics(
            hit_rate=result["metrics"]["hit_rate"],
            over_under_spread=result["metrics"]["over_under_spread"],
            steps=result["metrics"]["steps"]
        )
    )
