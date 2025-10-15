"""
Explainability endpoints (SHAP, PDP, interactions)
"""
from fastapi import APIRouter, Query, Depends

from app.models.schemas import (
    ExplainResponse, FeatureContribution, FeatureInteraction,
    ReliabilityBin
)
from app.services.explain import ExplainService
from app.deps import get_model_registry

router = APIRouter()


@router.get("", response_model=ExplainResponse)
async def get_explanation(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    registry = Depends(get_model_registry)
):
    """
    Get local explanation for a specific location and date.
    Returns SHAP values, interactions, and reliability information.
    
    TODO: Replace with actual SHAP computation on real data
    """
    explain_service = ExplainService(registry)
    
    # Compute local SHAP
    local_shap = explain_service.compute_local_shap(lat, lon, date)
    
    # Compute interactions (stub)
    interactions = explain_service.compute_interactions(lat, lon, date)
    
    # Get reliability bin
    probability = 0.35  # Stub
    reliability_bin = ReliabilityBin(
        range=(0.3, 0.4),
        observed=0.33
    )
    
    # Check for OOD
    ood = explain_service.check_ood(lat, lon, date)
    
    return ExplainResponse(
        probability=probability,
        ci=(0.25, 0.45),
        local_shap=local_shap,
        interactions=interactions,
        reliability_bin=reliability_bin,
        ood=ood
    )
