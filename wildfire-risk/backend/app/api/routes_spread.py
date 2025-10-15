from __future__ import annotations

from fastapi import APIRouter

from ..models.schemas import SpreadRequest, SpreadResponse
from ..services.spread import run_spread_simulation

router = APIRouter()


@router.post("/spread/run", response_model=SpreadResponse)
def run_spread(payload: SpreadRequest) -> SpreadResponse:
    return run_spread_simulation(payload)
