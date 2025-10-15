from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.services.shap_explainer import get_shap_values

router = APIRouter()


class ExplainRequest(BaseModel):
    """Request model for SHAP explanations"""
    latitude: float
    longitude: float
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    vegetation_index: float
    fuel_moisture: float


class FeatureImportance(BaseModel):
    """Feature importance for a single feature"""
    feature: str
    importance: float
    direction: str  # positive or negative


class ExplainResponse(BaseModel):
    """Response model for SHAP explanations"""
    base_value: float
    predicted_value: float
    feature_importances: List[FeatureImportance]


@router.post("/", response_model=ExplainResponse)
async def explain_prediction(request: ExplainRequest):
    """
    Generate SHAP-based explanations for risk prediction
    """
    try:
        features = {
            "temperature": request.temperature,
            "humidity": request.humidity,
            "wind_speed": request.wind_speed,
            "precipitation": request.precipitation,
            "vegetation_index": request.vegetation_index,
            "fuel_moisture": request.fuel_moisture
        }
        
        shap_values = get_shap_values(features)
        
        feature_importances = []
        for feature_name, shap_value in shap_values.items():
            direction = "positive" if shap_value > 0 else "negative"
            feature_importances.append(
                FeatureImportance(
                    feature=feature_name,
                    importance=abs(shap_value),
                    direction=direction
                )
            )
        
        # Sort by importance
        feature_importances.sort(key=lambda x: x.importance, reverse=True)
        
        return ExplainResponse(
            base_value=0.4,  # Placeholder for model base value
            predicted_value=0.65,  # Placeholder
            feature_importances=feature_importances
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
