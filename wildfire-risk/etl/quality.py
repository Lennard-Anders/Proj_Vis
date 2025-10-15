"""Synthetic data quality overlay generator."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dqf = {
        "date": date.today().isoformat(),
        "dqf_mask": [0, 1, 0],
        "data_availability": [0.9, 0.85, 0.93],
    }
    output = DATA_DIR / "quality.json"
    output.write_text(json.dumps(dqf, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
