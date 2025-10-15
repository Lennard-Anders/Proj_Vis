from __future__ import annotations

import random
from typing import Dict, List

from ..models.schemas import SpreadRequest, SpreadResponse


def run_spread_simulation(payload: SpreadRequest) -> SpreadResponse:
    rng = random.Random(hash(repr(payload.dict())))
    features: List[dict] = []
    base_points = _expand_points(payload.ignition_points)
    for step in range(payload.steps):
        ring = [
            [point["lon"] + 0.01 * step, point["lat"] + 0.01 * step]
            for point in base_points
        ]
        if ring and ring[0] != ring[-1]:
            ring.append(ring[0])
        features.append(
            {
                "type": "Feature",
                "properties": {"step": step},
                "geometry": {"type": "Polygon", "coordinates": [ring]},
            }
        )
    footprint = {"type": "FeatureCollection", "features": features}
    metrics = {
        "hit_rate": round(rng.uniform(0.6, 0.95), 2),
        "over_under_spread": round(rng.uniform(-0.1, 0.1), 2),
        "steps": payload.steps,
    }
    return SpreadResponse(footprint_geojson=footprint, metrics=metrics)


def _expand_points(points: List[Dict[str, float]]) -> List[Dict[str, float]]:
    if not points:
        return [{"lat": 0.0, "lon": 0.0}]
    return points
