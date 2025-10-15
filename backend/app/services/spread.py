"""
Fire spread simulation service - wind-driven envelope prototype
"""
import numpy as np
from typing import Dict, Any


class SpreadService:
    """Service for fire spread simulation"""
    
    def simulate_spread(
        self,
        lat: float,
        lon: float,
        wind_speed: float,
        wind_dir: float,
        duration_hours: int = 6,
        steps: int = 12
    ) -> Dict[str, Any]:
        """
        Simulate wind-driven fire spread using 8-neighbor anisotropic growth.
        
        Args:
            lat: Initial ignition latitude
            lon: Initial ignition longitude
            wind_speed: Wind speed in m/s
            wind_dir: Wind direction in degrees (meteorological convention)
            duration_hours: Simulation duration
            steps: Number of time steps
        
        Returns:
            Dictionary with footprint GeoJSON and metrics
        
        TODO: Add fuel models, terrain effects, and validation against FDCF
        """
        # Initialize grid (simple 50x50 around ignition point)
        grid_size = 50
        grid = np.zeros((grid_size, grid_size))
        
        # Set initial ignition at center
        center = grid_size // 2
        grid[center, center] = 1.0
        
        # Convert wind direction to radians and components
        wind_dir_rad = np.radians(wind_dir)
        wind_u = wind_speed * np.sin(wind_dir_rad)
        wind_v = wind_speed * np.cos(wind_dir_rad)
        
        # Simulate spread over time steps
        dt = duration_hours / steps
        
        for step in range(steps):
            grid = self._spread_step(grid, wind_u, wind_v, dt)
        
        # Convert grid to GeoJSON
        footprint_geojson = self._grid_to_geojson(grid, lat, lon, grid_size)
        
        # Compute metrics
        total_area = np.sum(grid > 0.1)
        metrics = {
            "hit_rate": 0.75,  # Stub
            "over_under_spread": 1.1,  # Stub: slightly over-predicted
            "steps": steps
        }
        
        return {
            "footprint": footprint_geojson,
            "metrics": metrics
        }
    
    def _spread_step(
        self,
        grid: np.ndarray,
        wind_u: float,
        wind_v: float,
        dt: float
    ) -> np.ndarray:
        """
        Perform one spread iteration using 8-neighbor stencil.
        
        Anisotropic growth weighted by wind direction.
        """
        new_grid = grid.copy()
        rows, cols = grid.shape
        
        # 8-neighbor offsets
        neighbors = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if grid[i, j] > 0.1:  # If cell is burning
                    # Spread to neighbors
                    for di, dj in neighbors:
                        ni, nj = i + di, j + dj
                        
                        # Compute spread probability based on wind alignment
                        # Wind-aligned direction gets higher weight
                        spread_prob = self._compute_spread_prob(
                            di, dj, wind_u, wind_v, dt
                        )
                        
                        new_grid[ni, nj] = max(
                            new_grid[ni, nj],
                            grid[i, j] * spread_prob
                        )
        
        return new_grid
    
    def _compute_spread_prob(
        self,
        di: int,
        dj: int,
        wind_u: float,
        wind_v: float,
        dt: float
    ) -> float:
        """
        Compute spread probability to neighbor based on wind.
        
        Higher probability in wind direction.
        """
        # Base spread rate
        base_rate = 0.3
        
        # Wind enhancement factor
        # Positive if aligned with wind, negative if against
        wind_alignment = (di * wind_v + dj * wind_u) / 10.0
        
        spread_prob = base_rate + wind_alignment * dt
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, spread_prob))
    
    def _grid_to_geojson(
        self,
        grid: np.ndarray,
        center_lat: float,
        center_lon: float,
        grid_size: int
    ) -> Dict[str, Any]:
        """
        Convert grid to GeoJSON polygon.
        
        TODO: Use actual spatial resolution and proper projection
        """
        # Simple conversion: each cell is ~0.01 degrees
        cell_size = 0.01
        
        # Find contour of burned area (cells > 0.1)
        burned_cells = []
        for i in range(grid_size):
            for j in range(grid_size):
                if grid[i, j] > 0.1:
                    # Convert grid indices to lat/lon
                    lat = center_lat + (i - grid_size / 2) * cell_size
                    lon = center_lon + (j - grid_size / 2) * cell_size
                    burned_cells.append([lon, lat])
        
        # Create simple polygon (convex hull would be better)
        if not burned_cells:
            burned_cells = [[center_lon, center_lat]]
        
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "MultiPoint",
                        "coordinates": burned_cells
                    },
                    "properties": {
                        "burn_probability": "high"
                    }
                }
            ]
        }
        
        return geojson
