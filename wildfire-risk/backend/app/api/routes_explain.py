from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends

from ..deps import get_registry
from ..models.registry import ModelBundleRegistry
from ..models.schemas import ExplainResponse
from ..services.explain import explain_point

router = APIRouter()


@router.get("/explain", response_model=ExplainResponse)
def get_explanation(
    lat: float,
    lon: float,
    date: date,
    registry: ModelBundleRegistry = Depends(get_registry),
) -> ExplainResponse:
    bundle = registry.get_bundle()
    return explain_point(lat, lon, date, bundle)
