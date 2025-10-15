"""
Pydantic schemas for all API endpoints
"""
from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field


class BBox(BaseModel):
    """Bounding box coordinates"""
    min_lon: float = Field(..., description="Minimum longitude")
    min_lat: float = Field(..., description="Minimum latitude")
    max_lon: float = Field(..., description="Maximum longitude")
    max_lat: float = Field(..., description="Maximum latitude")


class RiskTile(BaseModel):
    """Single risk tile with probability and confidence interval"""
    lat: float
    lon: float
    prob: float = Field(..., ge=0, le=1, description="Fire risk probability")
    ci: Tuple[float, float] = Field(..., description="Confidence interval [lower, upper]")


class QualityData(BaseModel):
    """Data quality indicators"""
    dqf_mask: List[int] = Field(default_factory=list, description="Data quality flags")
    data_availability: List[float] = Field(default_factory=list, description="Data availability 0-1")


class RiskRequest(BaseModel):
    """Request for risk assessment"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    bbox: Optional[BBox] = None


class RiskResponse(BaseModel):
    """Response with risk grid"""
    grid: List[RiskTile]
    quality: QualityData
    date: str
    bbox: BBox


class FeatureContribution(BaseModel):
    """SHAP-like feature contribution"""
    feature: str
    value: float
    unit: str
    contribution: float


class FeatureInteraction(BaseModel):
    """Feature interaction"""
    pair: Tuple[str, str]
    value: float


class ReliabilityBin(BaseModel):
    """Reliability calibration bin"""
    range: Tuple[float, float]
    observed: float


class ExplainRequest(BaseModel):
    """Request for explanation"""
    lat: float
    lon: float
    date: str


class ExplainResponse(BaseModel):
    """Response with local explanation"""
    probability: float
    ci: Tuple[float, float]
    local_shap: List[FeatureContribution]
    interactions: List[FeatureInteraction]
    reliability_bin: ReliabilityBin
    ood: bool


class FeatureDelta(BaseModel):
    """Feature delta or override"""
    wind_speed_10m: Optional[float] = None
    rh: Optional[float] = None
    rain_24h: Optional[float] = None
    gust_10m: Optional[float] = None


class CounterfactualRequest(BaseModel):
    """Request for counterfactual analysis"""
    lat: float
    lon: float
    date: str
    deltas: FeatureDelta
    use_surrogate: bool = True


class ReasonCodeDelta(BaseModel):
    """Change in reason code"""
    feature: str
    delta_contribution: float


class CounterfactualResponse(BaseModel):
    """Response with counterfactual result"""
    probability: float
    delta: float
    reason_codes_delta: List[ReasonCodeDelta]
    used: str = Field(..., description="'surrogate' or 'full'")


class FramesRequest(BaseModel):
    """Request for FDCF frames"""
    event_id: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    date: Optional[str] = None


class FramesResponse(BaseModel):
    """Response with frame metadata"""
    times: List[str]
    tiles: List[str]


class SpreadRequest(BaseModel):
    """Request for fire spread simulation"""
    lat: float
    lon: float
    date: str
    wind_speed_10m: float
    wind_dir: float
    duration_hours: int = 6
    steps: int = 12


class SpreadMetrics(BaseModel):
    """Spread simulation metrics"""
    hit_rate: float
    over_under_spread: float
    steps: int


class SpreadResponse(BaseModel):
    """Response with spread footprint"""
    footprint_geojson: Dict[str, Any]
    metrics: SpreadMetrics
