"""
Tile indexing and bounding box helpers
"""
import math
from typing import Tuple, List


def latlon_to_tile(lat: float, lon: float, resolution: float = 0.25) -> Tuple[int, int]:
    """
    Convert lat/lon to tile indices.
    
    Args:
        lat: Latitude
        lon: Longitude
        resolution: Tile resolution in degrees
    
    Returns:
        Tuple of (tile_lat_index, tile_lon_index)
    """
    tile_lat = int(math.floor(lat / resolution))
    tile_lon = int(math.floor(lon / resolution))
    return tile_lat, tile_lon


def tile_to_latlon(tile_lat: int, tile_lon: int, resolution: float = 0.25) -> Tuple[float, float]:
    """
    Convert tile indices to center lat/lon.
    
    Args:
        tile_lat: Tile latitude index
        tile_lon: Tile longitude index
        resolution: Tile resolution in degrees
    
    Returns:
        Tuple of (lat, lon) at tile center
    """
    lat = (tile_lat + 0.5) * resolution
    lon = (tile_lon + 0.5) * resolution
    return lat, lon


def bbox_to_tiles(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    resolution: float = 0.25
) -> List[Tuple[int, int]]:
    """
    Get all tiles within a bounding box.
    
    Args:
        min_lat: Minimum latitude
        min_lon: Minimum longitude
        max_lat: Maximum latitude
        max_lon: Maximum longitude
        resolution: Tile resolution in degrees
    
    Returns:
        List of (tile_lat, tile_lon) tuples
    """
    tiles = []
    
    # Get tile indices for corners
    min_tile_lat, min_tile_lon = latlon_to_tile(min_lat, min_lon, resolution)
    max_tile_lat, max_tile_lon = latlon_to_tile(max_lat, max_lon, resolution)
    
    # Iterate over all tiles in bbox
    for tile_lat in range(min_tile_lat, max_tile_lat + 1):
        for tile_lon in range(min_tile_lon, max_tile_lon + 1):
            tiles.append((tile_lat, tile_lon))
    
    return tiles


def tile_to_bbox(
    tile_lat: int,
    tile_lon: int,
    resolution: float = 0.25
) -> Tuple[float, float, float, float]:
    """
    Get bounding box for a tile.
    
    Args:
        tile_lat: Tile latitude index
        tile_lon: Tile longitude index
        resolution: Tile resolution in degrees
    
    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat)
    """
    min_lat = tile_lat * resolution
    min_lon = tile_lon * resolution
    max_lat = (tile_lat + 1) * resolution
    max_lon = (tile_lon + 1) * resolution
    
    return min_lon, min_lat, max_lon, max_lat
