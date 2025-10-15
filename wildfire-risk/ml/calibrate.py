"""Stub calibration pipeline that refreshes calibration metadata."""

from __future__ import annotations

import json
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parents[1] / "backend" / "models" / "bundles" / "current"


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    calibration = {
        "global": {"method": "platt", "a": 0.9, "b": 0.05},
        "regions": {
            "west": {"method": "isotonic", "slope": [0.0, 0.5, 1.0]},
        },
    }
    output = MODEL_DIR / "calibration.json"
    output.write_text(json.dumps(calibration, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
