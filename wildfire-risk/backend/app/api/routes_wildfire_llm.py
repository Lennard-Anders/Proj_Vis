from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field

from ..services.llm_wildfire import estimate_wildfire_risk_llm, list_local_llm_models


class WildfireLlmResponse(BaseModel):
    wildfire_probability_percent: int = Field(..., ge=0, le=100)
    explanation: str

router = APIRouter(prefix="/wildfire-llm", tags=["wildfire-llm"])


@router.get("/risk", response_model=WildfireLlmResponse)
async def get_wildfire_risk_llm(
    temperature_c: float = Query(..., description="Air temperature in °C"),
    wind_speed_kmh: float = Query(..., description="Wind speed in km/h"),
    relative_humidity_percent: float = Query(
        ..., ge=0, le=100, description="Relative humidity in %"
    ),
    rain_last_24h_mm: float = Query(
        ..., ge=0, description="Rainfall during the last 24 hours in mm"
    ),
    model: str | None = Query(None, description="Optional model name"),
    lat: float | None = Query(None, ge=-90, le=90, description="Latitude for location-aware prompt"),
    lon: float | None = Query(None, ge=-180, le=180, description="Longitude for location-aware prompt"),
) -> Dict[str, Any]:
    """Estimate wildfire risk using the local LLM (Ollama).

    Returns JSON with:
    - wildfire_probability_percent: integer 0-100
    - explanation: English explanation string
    """

    try:
        result = await estimate_wildfire_risk_llm(
            temperature_c=temperature_c,
            wind_speed_kmh=wind_speed_kmh,
            relative_humidity_percent=relative_humidity_percent,
            rain_last_24h_mm=rain_last_24h_mm,
            model=model,
            latitude=lat,
            longitude=lon,
        )
    except Exception as exc:  # noqa: BLE001
        # Avoid leaking internal errors; surface as 502 to caller
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Wildfire LLM service unavailable",
        ) from exc

    return result


@router.get("/models", response_model=list[str])
async def list_wildfire_llm_models() -> list[str]:
    return await list_local_llm_models()
