from __future__ import annotations

from datetime import date

from fastapi import APIRouter

from ..models.schemas import FramesResponse
from ..services.frames import list_frames

router = APIRouter()


@router.get("/frames", response_model=FramesResponse)
def get_frames(lat: float, lon: float, date: date) -> FramesResponse:
    return list_frames(lat, lon, date)
