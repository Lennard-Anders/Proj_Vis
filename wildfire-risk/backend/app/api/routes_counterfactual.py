from __future__ import annotations

from fastapi import APIRouter, Depends

from ..deps import get_registry
from ..models.registry import ModelBundleRegistry
from ..models.schemas import CounterfactualRequest, CounterfactualResponse
from ..services.counterfactual import run_counterfactual

router = APIRouter()


@router.post("/risk/counterfactual", response_model=CounterfactualResponse)
def post_counterfactual(
    payload: CounterfactualRequest,
    registry: ModelBundleRegistry = Depends(get_registry),
) -> CounterfactualResponse:
    bundle = registry.get_bundle()
    return run_counterfactual(payload, bundle)
