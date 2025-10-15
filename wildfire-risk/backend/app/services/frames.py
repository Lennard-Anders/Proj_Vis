from __future__ import annotations

import random
from datetime import date

from ..models.schemas import FrameItem, FramesResponse


def list_frames(lat: float, lon: float, target_date: date) -> FramesResponse:
    rng = random.Random(hash((lat, lon, target_date.isoformat())))
    items = []
    for idx in range(3):
        ts = target_date.strftime("%Y-%m-%d") + f"T0{idx}:00:00Z"
        items.append(
            FrameItem(
                frame_id=f"fdcf-{idx}",
                timestamp=ts,
                url=f"https://example.com/frames/{lat:.2f}_{lon:.2f}_{idx}.png",
                cloud_coverage=round(rng.uniform(0.0, 0.4), 2),
            )
        )
    return FramesResponse(frames=items)
