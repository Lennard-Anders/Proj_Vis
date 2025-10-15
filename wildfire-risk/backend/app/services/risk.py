from __future__ import annotations

import math
import random
from datetime import date
from typing import List

from ..models.registry import ModelBundle
from ..models.schemas import BoundingBox, RiskGridCell, RiskMeta, RiskQuality, RiskResponse


def _frange(start: float, stop: float, step: float) -> List[float]:
    count = max(int(math.ceil((stop - start) / step)), 1)
    return [start + i * step for i in range(count)]


def score_tile(bbox: BoundingBox, target_date: date, bundle: ModelBundle) -> RiskResponse:
    grid_cells: List[RiskGridCell] = []
    rng = random.Random(hash((target_date.isoformat(), bbox.min_lat, bbox.min_lon)))
    latitudes = _frange(bbox.min_lat, bbox.max_lat, 0.25)
    longitudes = _frange(bbox.min_lon, bbox.max_lon, 0.25)

    for lat in latitudes:
        for lon in longitudes:
            base_prob = 0.15 + 0.2 * math.sin(math.radians(lat + lon))
            wind_effect = rng.uniform(-0.05, 0.1)
            rh_effect = rng.uniform(-0.1, 0.05)
            prob = min(max(base_prob + wind_effect - rh_effect, 0.01), 0.99)
            ci = (max(prob - 0.05, 0.0), min(prob + 0.05, 1.0))
            grid_cells.append(RiskGridCell(lat=round(lat, 3), lon=round(lon, 3), prob=round(prob, 3), ci=ci))

    quality = RiskQuality(
        dqf_mask=[rng.randint(0, 1) for _ in range(len(grid_cells))],
        data_availability=[round(rng.uniform(0.85, 1.0), 2) for _ in range(len(grid_cells))],
    )

    meta = RiskMeta(grid_deg=0.25, generated_at=target_date)
    return RiskResponse(grid=grid_cells, quality=quality, meta=meta)
