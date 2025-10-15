"""Stub SHAP report generator."""

from __future__ import annotations

import json
from pathlib import Path

REPORT_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "global_importance": [
            {"feature": "wind_speed_10m", "importance": 0.32},
            {"feature": "rh", "importance": 0.21},
            {"feature": "rain_24h", "importance": 0.12},
        ],
        "interactions": [{"pair": ["rh", "wind_speed_10m"], "strength": 0.05}],
    }
    output = REPORT_DIR / "shap_report.json"
    output.write_text(json.dumps(report, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
