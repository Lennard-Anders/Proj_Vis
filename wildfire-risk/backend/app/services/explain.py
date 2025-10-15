from __future__ import annotations

import random
from datetime import date

from ..models.registry import ModelBundle
from ..models.schemas import ExplainInteraction, ExplainLocalShap, ExplainResponse, ReliabilityBin


def explain_point(lat: float, lon: float, target_date: date, bundle: ModelBundle) -> ExplainResponse:
    rng = random.Random(hash((lat, lon, target_date.isoformat())))
    probability = rng.uniform(0.05, 0.7)
    shap_values = [
        ExplainLocalShap(feature="rh", value=rng.uniform(10, 40), unit="%", contribution=rng.uniform(-0.1, 0.1)),
        ExplainLocalShap(
            feature="wind_speed_10m", value=rng.uniform(0, 25), unit="m/s", contribution=rng.uniform(-0.05, 0.15)
        ),
        ExplainLocalShap(feature="rain_24h", value=rng.uniform(0, 10), unit="mm", contribution=rng.uniform(-0.08, 0.02)),
    ]
    interactions = [
        ExplainInteraction(pair=("rh", "wind_speed_10m"), value=rng.uniform(-0.05, 0.08)),
        ExplainInteraction(pair=("rain_24h", "vpd"), value=rng.uniform(-0.03, 0.05)),
    ]
    reliability = ReliabilityBin(range=(0.25, 0.30), observed=round(probability * rng.uniform(0.9, 1.1), 3))
    ood = rng.choice([False, False, False, True])
    return ExplainResponse(
        probability=round(probability, 3),
        ci=(max(probability - 0.05, 0.0), min(probability + 0.05, 1.0)),
        local_shap=shap_values,
        interactions=interactions,
        reliability_bin=reliability,
        ood=ood,
    )
