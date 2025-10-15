"""Stub ETL that fabricates FDCF frame metadata."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sample"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    frames = [
        {
            "frame_id": f"fdcf-{idx}",
            "lat": 35.0 + idx * 0.1,
            "lon": -120.0 - idx * 0.1,
            "date": date.today().isoformat(),
            "cloud_score": 0.1 * idx,
        }
        for idx in range(3)
    ]
    output = DATA_DIR / "fdcf_frames.json"
    output.write_text(json.dumps(frames, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
