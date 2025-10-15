"""
Counterfactual "what-if" analysis endpoints
"""
from fastapi import APIRouter, Depends

from app.models.schemas import (
    CounterfactualRequest, CounterfactualResponse,
    ReasonCodeDelta
)
from app.services.counterfactual import CounterfactualService
from app.deps import get_model_registry

router = APIRouter()


@router.post("/counterfactual", response_model=CounterfactualResponse)
async def compute_counterfactual(
    request: CounterfactualRequest,
    registry = Depends(get_model_registry)
):
    """
    Compute counterfactual risk given feature deltas.
    
    Supports two paths:
    - Surrogate: Fast GLM/GBM emulator (default)
    - Full: Complete model re-scoring (slower but accurate)
    
    TODO: Implement actual surrogate and full model paths
    """
    cf_service = CounterfactualService(registry)
    
    if request.use_surrogate:
        result = cf_service.fast_surrogate(
            request.lat,
            request.lon,
            request.date,
            request.deltas
        )
        used = "surrogate"
    else:
        result = cf_service.primary_full_rescore(
            request.lat,
            request.lon,
            request.date,
            request.deltas
        )
        used = "full"
    
    return CounterfactualResponse(
        probability=result["probability"],
        delta=result["delta"],
        reason_codes_delta=result["reason_codes_delta"],
        used=used
    )
