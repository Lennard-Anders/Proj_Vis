from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.model_loader import get_model
from app.services.calibration import apply_calibration

router = APIRouter()


class RiskRequest(BaseModel):
    """Request model for risk prediction"""
    latitude: float
    longitude: float
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    vegetation_index: float
    fuel_moisture: float


class RiskResponse(BaseModel):
    """Response model for risk prediction"""
    risk_score: float
    risk_level: str
    confidence: float
    calibrated_score: float


class CounterfactualRequest(BaseModel):
    """Request model for counterfactual analysis"""
    latitude: float
    longitude: float
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    vegetation_index: float
    fuel_moisture: float
    target_risk: float


class CounterfactualResponse(BaseModel):
    """Response model for counterfactual analysis"""
    original_risk: float
    target_risk: float
    suggested_changes: dict
    feasibility: float


@router.post("/", response_model=RiskResponse)
async def predict_risk(request: RiskRequest):
    """
    Predict wildfire risk based on environmental conditions
    """
    try:
        model = get_model()
        features = [
            request.temperature,
            request.humidity,
            request.wind_speed,
            request.precipitation,
            request.vegetation_index,
            request.fuel_moisture
        ]
        
        raw_score = model.predict([features])[0]
        calibrated_score = apply_calibration(raw_score)
        
        # Determine risk level
        if calibrated_score < 0.3:
            risk_level = "low"
        elif calibrated_score < 0.6:
            risk_level = "moderate"
        elif calibrated_score < 0.8:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return RiskResponse(
            risk_score=raw_score,
            risk_level=risk_level,
            confidence=0.85,  # Placeholder
            calibrated_score=calibrated_score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/counterfactual", response_model=CounterfactualResponse)
async def generate_counterfactual(request: CounterfactualRequest):
    """
    Generate counterfactual explanations - what changes would achieve target risk
    """
    try:
        model = get_model()
        features = [
            request.temperature,
            request.humidity,
            request.wind_speed,
            request.precipitation,
            request.vegetation_index,
            request.fuel_moisture
        ]
        
        original_risk = model.predict([features])[0]
        
        # Simple heuristic for counterfactual - in production use proper CF algorithm
        suggested_changes = {
            "humidity": "+10%",
            "precipitation": "+5mm",
            "wind_speed": "-2m/s"
        }
        
        return CounterfactualResponse(
            original_risk=original_risk,
            target_risk=request.target_risk,
            suggested_changes=suggested_changes,
            feasibility=0.75
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
