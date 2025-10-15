from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from joblib import dump, load


@dataclass
class SurrogateModel:
    """Tiny surrogate emulator for interactive counterfactuals."""

    coefficients: Dict[str, float]
    intercept: float

    def predict(self, features: Dict[str, float]) -> float:
        score = self.intercept
        for name, value in features.items():
            score += self.coefficients.get(name, 0.0) * value
        return max(0.0, min(1.0, score))


@dataclass
class ModelBundle:
    path: Path
    feature_order: List[str] = field(default_factory=list)
    calibration: Dict[str, Any] = field(default_factory=dict)
    training_ranges: Dict[str, Any] = field(default_factory=dict)
    surrogate: SurrogateModel | None = None

    def refresh(self) -> None:
        self.feature_order = self._load_json("feature_order.json", default=[])
        self.calibration = self._load_json("calibration.json", default={})
        self.training_ranges = self._load_json("training_ranges.json", default={})
        self.surrogate = self._load_surrogate()

    def _load_json(self, name: str, default: Any) -> Any:
        file_path = self.path / name
        if not file_path.exists():
            return default
        return json.loads(file_path.read_text())

    def _load_surrogate(self) -> SurrogateModel | None:
        model_path = self.path / "surrogate.joblib"
        if not model_path.exists():
            return None
        data = load(model_path)
        if isinstance(data, SurrogateModel):
            return data
        if isinstance(data, dict):
            return SurrogateModel(
                coefficients=data.get("coefficients", {}),
                intercept=data.get("intercept", 0.0),
            )
        return None


class ModelBundleRegistry:
    def __init__(self, bundle_path: str) -> None:
        self.bundle_path = Path(bundle_path)
        self.bundle = ModelBundle(path=self.bundle_path)
        self._ensure_stub_assets()
        self.bundle.refresh()

    def _ensure_stub_assets(self) -> None:
        self.bundle_path.mkdir(parents=True, exist_ok=True)
        feature_file = self.bundle_path / "feature_order.json"
        if not feature_file.exists():
            feature_file.write_text(json.dumps(["wind_speed_10m", "rh", "rain_24h"]))
        calibration_file = self.bundle_path / "calibration.json"
        if not calibration_file.exists():
            calibration_file.write_text(json.dumps({"global": {"method": "platt", "a": 1.0, "b": 0.0}}))
        ranges_file = self.bundle_path / "training_ranges.json"
        if not ranges_file.exists():
            ranges_file.write_text(json.dumps({"wind_speed_10m": {"min": 0, "max": 40}}))
        surrogate_file = self.bundle_path / "surrogate.joblib"
        if not surrogate_file.exists():
            dump(
                SurrogateModel(coefficients={"rh": -0.003, "wind_speed_10m": 0.01}, intercept=0.2),
                surrogate_file,
            )

    def get_bundle(self) -> ModelBundle:
        return self.bundle

    def reload(self) -> None:
        self.bundle.refresh()
