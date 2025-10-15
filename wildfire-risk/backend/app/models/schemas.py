from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class BoundingBox(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    @validator("max_lon")
    def lon_range(cls, value: float, values: dict[str, float]) -> float:  # type: ignore[override]
        min_lon = values.get("min_lon", -180.0)
        if value <= min_lon:
            raise ValueError("max_lon must be greater than min_lon")
        return value

    @validator("max_lat")
    def lat_range(cls, value: float, values: dict[str, float]) -> float:  # type: ignore[override]
        min_lat = values.get("min_lat", -90.0)
        if value <= min_lat:
            raise ValueError("max_lat must be greater than min_lat")
        return value


class RiskGridCell(BaseModel):
    lat: float
    lon: float
    prob: float = Field(ge=0.0, le=1.0)
    ci: tuple[float, float]


class RiskQuality(BaseModel):
    dqf_mask: List[int]
    data_availability: List[float]


class RiskMeta(BaseModel):
    grid_deg: float = 0.25
    generated_at: date | None = None


class RiskResponse(BaseModel):
    grid: List[RiskGridCell]
    quality: RiskQuality
    meta: RiskMeta


class ExplainLocalShap(BaseModel):
    feature: str
    value: float
    unit: str
    contribution: float


class ExplainInteraction(BaseModel):
    pair: tuple[str, str]
    value: float


class ReliabilityBin(BaseModel):
    range: tuple[float, float]
    observed: float


class ExplainResponse(BaseModel):
    probability: float
    ci: tuple[float, float]
    local_shap: List[ExplainLocalShap]
    interactions: List[ExplainInteraction]
    reliability_bin: ReliabilityBin
    ood: bool


class CounterfactualRequest(BaseModel):
    lat: float
    lon: float
    date: date
    overrides: dict[str, float]
    use_full_model: bool = False


class ReasonCodeDelta(BaseModel):
    feature: str
    from_: float = Field(alias="from")
    to: float
    d_contribution: float

    class Config:
        allow_population_by_field_name = True


class CounterfactualResponse(BaseModel):
    probability: float
    delta: float
    reason_codes_delta: List[ReasonCodeDelta]
    used: str


class FrameItem(BaseModel):
    frame_id: str
    timestamp: str
    url: str
    cloud_coverage: float


class FramesResponse(BaseModel):
    frames: List[FrameItem]


class SpreadRequest(BaseModel):
    ignition_points: List[dict[str, float]]
    wind_speed_10m: float
    wind_dir: float
    steps: int = 10


class SpreadResponse(BaseModel):
    footprint_geojson: dict
    metrics: dict
