from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Query

from ..services.llm_wildfire import estimate_wildfire_risk_llm

router = APIRouter(prefix="/wildfire-llm", tags=["wildfire-llm"])


@router.get("/risk", response_model=dict)
async def get_wildfire_risk_llm(
    temperature_c: float = Query(..., description="Air temperature in °C"),
    wind_speed_kmh: float = Query(..., description="Wind speed in km/h"),
    relative_humidity_percent: float = Query(
        ..., ge=0, le=100, description="Relative humidity in %"
    ),
    rain_last_24h_mm: float = Query(
        ..., ge=0, description="Rainfall during the last 24 hours in mm"
    ),
) -> Dict[str, Any]:
    """Estimate wildfire risk using the local LLM (Ollama).

    Returns JSON with:
    - wildfire_probability_percent: integer 0-100
    - explanation: English explanation string
    """

    result = await estimate_wildfire_risk_llm(
        temperature_c=temperature_c,
        wind_speed_kmh=wind_speed_kmh,
        relative_humidity_percent=relative_humidity_percent,
        rain_last_24h_mm=rain_last_24h_mm,
    )

    return result
