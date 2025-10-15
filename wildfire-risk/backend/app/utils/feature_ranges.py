from __future__ import annotations

from typing import Dict


def in_training_range(value: float, ranges: Dict[str, Dict[str, float]], feature: str) -> bool:
    feature_range = ranges.get(feature)
    if not feature_range:
        return True
    minimum = feature_range.get("min", float("-inf"))
    maximum = feature_range.get("max", float("inf"))
    return minimum <= value <= maximum
