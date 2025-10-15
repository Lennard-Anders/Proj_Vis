"""Stub bundler ensuring all artifacts exist in the current bundle."""

from __future__ import annotations

import json
from pathlib import Path

from joblib import dump

MODEL_DIR = Path(__file__).resolve().parents[1] / "backend" / "models" / "bundles" / "current"


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    feature_order = ["wind_speed_10m", "rh", "rain_24h", "gust_10m", "wind_dir"]
    (MODEL_DIR / "feature_order.json").write_text(json.dumps(feature_order, indent=2))

    training_ranges = {
        "wind_speed_10m": {"min": 0, "max": 45},
        "rh": {"min": 0, "max": 100},
        "rain_24h": {"min": 0, "max": 200},
    }
    (MODEL_DIR / "training_ranges.json").write_text(json.dumps(training_ranges, indent=2))

    shap_bg = [{"wind_speed_10m": 5.0, "rh": 30.0, "rain_24h": 0.5}]
    dump(shap_bg, MODEL_DIR / "shap_bg.joblib")

    booster = MODEL_DIR / "booster.bin"
    if not booster.exists():
        booster.write_text("synthetic booster placeholder")

    print(f"bundle refreshed at {MODEL_DIR}")


if __name__ == "__main__":
    main()
