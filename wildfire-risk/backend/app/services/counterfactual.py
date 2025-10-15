from __future__ import annotations

import random
from typing import Dict

from ..models.registry import ModelBundle
from ..models.schemas import CounterfactualRequest, CounterfactualResponse, ReasonCodeDelta


def run_counterfactual(request: CounterfactualRequest, bundle: ModelBundle) -> CounterfactualResponse:
    rng = random.Random(hash((request.lat, request.lon, request.date.isoformat())))
    base_probability = rng.uniform(0.2, 0.6)
    overrides = request.overrides

    surrogate_used = False
    if bundle.surrogate and not request.use_full_model:
        surrogate_used = True
        prob_delta = _predict_delta_with_surrogate(bundle, overrides)
    else:
        prob_delta = _simulate_full_rescore(rng, overrides)

    new_probability = max(0.01, min(0.99, base_probability + prob_delta))
    reason_codes = _build_reason_codes(overrides, prob_delta)

    return CounterfactualResponse(
        probability=round(new_probability, 3),
        delta=round(prob_delta, 3),
        reason_codes_delta=reason_codes,
        used="surrogate" if surrogate_used else "full",
    )


def _predict_delta_with_surrogate(bundle: ModelBundle, overrides: Dict[str, float]) -> float:
    surrogate = bundle.surrogate
    if surrogate is None:
        return 0.0
    return surrogate.predict(overrides) - surrogate.intercept


def _simulate_full_rescore(rng: random.Random, overrides: Dict[str, float]) -> float:
    total_effect = 0.0
    for name, value in overrides.items():
        modifier = 0.0
        if "wind" in name:
            modifier = 0.01 * value
        elif name == "rh":
            modifier = -0.002 * value
        elif "rain" in name:
            modifier = -0.001 * value
        total_effect += modifier
    total_effect += rng.uniform(-0.05, 0.05)
    return total_effect


def _build_reason_codes(overrides: Dict[str, float], prob_delta: float) -> list[ReasonCodeDelta]:
    if not overrides:
        return []
    per_feature_delta = prob_delta / max(len(overrides), 1)
    reason_codes: list[ReasonCodeDelta] = []
    for feature, target_value in overrides.items():
        reason_codes.append(
            ReasonCodeDelta(
                feature=feature,
                from_=target_value - per_feature_delta * 100,
                to=target_value,
                d_contribution=round(per_feature_delta, 3),
            )
        )
    return reason_codes
