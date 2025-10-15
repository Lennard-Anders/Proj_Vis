"""Stub weather ingestion that emits synthetic meteorology tiles."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = DATA_DIR / "weather_tiles.csv"
    with output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["date", "lat", "lon", "wind_speed_10m", "rh", "rain_24h"])
        writer.writeheader()
        for idx in range(5):
            writer.writerow(
                {
                    "date": date.today().isoformat(),
                    "lat": 35.0 + 0.25 * idx,
                    "lon": -120.0 + 0.25 * idx,
                    "wind_speed_10m": 5 + idx,
                    "rh": 20 + idx,
                    "rain_24h": idx * 0.5,
                }
            )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
