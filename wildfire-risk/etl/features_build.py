"""Stub feature builder combining weather + labels."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = DATA_DIR / "features.csv"

    with output.open("w", newline="") as fh:
        fieldnames = [
            "date",
            "lat",
            "lon",
            "wind_speed_10m",
            "rh",
            "rain_24h",
            "ignition",
            "dqf_mask",
            "data_availability",
        ]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for idx in range(5):
            writer.writerow(
                {
                    "date": date.today().isoformat(),
                    "lat": 35.0 + 0.25 * idx,
                    "lon": -120.0 + 0.25 * idx,
                    "wind_speed_10m": 5 + idx,
                    "rh": 20 + idx * 3,
                    "rain_24h": idx * 0.2,
                    "ignition": int(idx % 2 == 0),
                    "dqf_mask": 0,
                    "data_availability": 0.95,
                }
            )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
