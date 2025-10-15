"""Stub labeler that flags ignition events from synthetic masks."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = DATA_DIR / "ignitions.csv"
    with output.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["date", "lat", "lon", "ignition"])
        writer.writeheader()
        for idx in range(5):
            writer.writerow(
                {
                    "date": date.today().isoformat(),
                    "lat": 35.0 + 0.25 * idx,
                    "lon": -120.0 + 0.25 * idx,
                    "ignition": int(idx % 2 == 0),
                }
            )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
