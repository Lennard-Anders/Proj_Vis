from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Tile:
    lat: float
    lon: float


def iter_tiles(min_lat: float, min_lon: float, max_lat: float, max_lon: float, step: float = 0.25) -> Iterable[Tile]:
    lat = min_lat
    while lat < max_lat + 1e-6:
        lon = min_lon
        while lon < max_lon + 1e-6:
            yield Tile(lat=round(lat, 3), lon=round(lon, 3))
            lon += step
        lat += step
