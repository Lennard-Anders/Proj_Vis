"""AI-powered wildfire risk prediction API routes."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import date

from ..services.ai_risk import wildfire_predictor
from ..services.temperature import temperature_service

router = APIRouter(prefix="/ai-risk", tags=["ai-risk"])


class RiskPredictionRequest(BaseModel):
    """Request for AI risk prediction."""
    latitude: float
    longitude: float
    temperature: float
    wind_speed_10m: float
    rh: float  # relative humidity
    rain_24h: float = 0.0
    date: Optional[str] = None
    use_historical_context: bool = True


class RiskGridRequest(BaseModel):
    """Request for grid-based risk prediction."""
    center_lat: float
    center_lon: float
    grid_size_deg: float = 1.0
    grid_resolution: int = 20
    temperature: float
    wind_speed_10m: float
    rh: float
    rain_24h: float = 0.0


class ContributingFactor(BaseModel):
    """Contributing factor to wildfire risk."""
    factor: str
    contribution: float
    impact: str


class RiskPredictionResponse(BaseModel):
    """AI risk prediction response."""
    probability: float
    risk_level: str
    risk_color: str
    contributing_factors: List[ContributingFactor]
    recommendations: List[str]
    confidence: float
    features: Dict[str, float]


class GridCell(BaseModel):
    """Grid cell with risk prediction."""
    latitude: float
    longitude: float
    probability: float
    risk_level: str
    risk_color: str


class RiskGridResponse(BaseModel):
    """Grid-based risk prediction response."""
    grid_cells: List[GridCell]
    center_lat: float
    center_lon: float
    grid_size_deg: float
    resolution: int


@router.post("/predict", response_model=RiskPredictionResponse)
async def predict_wildfire_risk(request: RiskPredictionRequest):
    """
    Predict wildfire risk using AI model based on weather conditions.
    
    This endpoint uses machine learning to calculate wildfire probability
    based on temperature, wind, humidity, rainfall, and historical patterns.
    
    Parameters:
    - latitude, longitude: Location coordinates
    - temperature: Current temperature in °C
    - wind_speed_10m: Wind speed at 10m height in m/s
    - rh: Relative humidity in %
    - rain_24h: 24-hour rainfall in mm (default: 0)
    - date: Optional date for historical context
    - use_historical_context: Whether to use historical temperature data
    """
    try:
        # Get historical context if requested
        historical_mean_temp = None
        if request.use_historical_context:
            historical_stats = temperature_service.get_historical_stats(
                request.latitude,
                request.longitude,
                radius_km=50
            )
            historical_mean_temp = historical_stats.get('mean_temp')
        
        # Predict risk
        prediction = wildfire_predictor.predict_risk(
            latitude=request.latitude,
            longitude=request.longitude,
            temperature=request.temperature,
            wind_speed_10m=request.wind_speed_10m,
            rh=request.rh,
            rain_24h=request.rain_24h,
            historical_mean_temp=historical_mean_temp,
            date=request.date
        )
        
        return RiskPredictionResponse(**prediction)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting wildfire risk: {str(e)}"
        )


@router.post("/predict-grid", response_model=RiskGridResponse)
async def predict_risk_grid(request: RiskGridRequest):
    """
    Predict wildfire risk for a grid of locations around a center point.
    
    This creates a spatial heatmap of wildfire risk based on the provided
    weather parameters, with natural spatial variation.
    
    Parameters:
    - center_lat, center_lon: Center point coordinates
    - grid_size_deg: Grid size in degrees (default: 1.0)
    - grid_resolution: Number of cells per side (default: 20)
    - temperature: Base temperature in °C
    - wind_speed_10m: Base wind speed in m/s
    - rh: Base relative humidity in %
    - rain_24h: 24-hour rainfall in mm (default: 0)
    """
    try:
        # Get historical stats for the area
        historical_stats = temperature_service.get_historical_stats(
            request.center_lat,
            request.center_lon,
            radius_km=100
        )
        
        # Prepare base parameters
        base_params = {
            'temperature': request.temperature,
            'wind_speed_10m': request.wind_speed_10m,
            'rh': request.rh,
            'rain_24h': request.rain_24h
        }
        
        # Predict grid
        grid_cells = wildfire_predictor.predict_grid_risk(
            center_lat=request.center_lat,
            center_lon=request.center_lon,
            grid_size_deg=request.grid_size_deg,
            grid_resolution=request.grid_resolution,
            base_params=base_params,
            historical_stats=historical_stats
        )
        
        return RiskGridResponse(
            grid_cells=grid_cells,
            center_lat=request.center_lat,
            center_lon=request.center_lon,
            grid_size_deg=request.grid_size_deg,
            resolution=request.grid_resolution
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting risk grid: {str(e)}"
        )
