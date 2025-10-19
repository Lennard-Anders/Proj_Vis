from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_registry
from ..models.registry import ModelBundleRegistry
from ..models.schemas import BoundingBox, RiskResponse
from ..services.risk import score_tile

router = APIRouter()


def _parse_bbox(raw: str) -> BoundingBox:
    parts = raw.split(",")
    if len(parts) != 4:
        raise ValueError("bbox must contain four comma-separated values")
    min_lon, min_lat, max_lon, max_lat = map(float, parts)
    if max_lon <= min_lon:
        raise ValueError("max_lon must be greater than min_lon")
    if max_lat <= min_lat:
        raise ValueError("max_lat must be greater than min_lat")
    return BoundingBox(min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)


@router.get("/risk", response_model=RiskResponse)
def get_risk(
    date: date,
    bbox: str,
    registry: ModelBundleRegistry = Depends(get_registry),
) -> RiskResponse:
    try:
        bounds = _parse_bbox(bbox)
    except ValueError as exc:  # pragma: no cover - simple validation message
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    bundle = registry.get_bundle()
    return score_tile(bounds, date, bundle)
