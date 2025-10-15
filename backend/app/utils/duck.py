"""
DuckDB helpers for efficient feature queries
"""
import duckdb
from typing import Optional, List, Dict, Any
from pathlib import Path


class DuckDBHelper:
    """Helper class for DuckDB operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize DuckDB connection.
        
        Args:
            db_path: Path to DuckDB database file. If None, use in-memory.
        """
        if db_path:
            self.conn = duckdb.connect(db_path)
        else:
            self.conn = duckdb.connect(":memory:")
    
    def register_parquet(self, name: str, path: str):
        """
        Register a Parquet file or directory as a table.
        
        Args:
            name: Table name to register
            path: Path to Parquet file or directory
        """
        self.conn.execute(f"""
            CREATE OR REPLACE VIEW {name} AS
            SELECT * FROM read_parquet('{path}')
        """)
    
    def query_features_by_bbox(
        self,
        table: str,
        date: str,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float
    ) -> List[Dict[str, Any]]:
        """
        Query features within a bounding box for a specific date.
        
        Args:
            table: Table name
            date: Date string (YYYY-MM-DD)
            min_lat: Minimum latitude
            min_lon: Minimum longitude
            max_lat: Maximum latitude
            max_lon: Maximum longitude
        
        Returns:
            List of feature dictionaries
        """
        query = f"""
            SELECT *
            FROM {table}
            WHERE date = '{date}'
              AND lat >= {min_lat} AND lat <= {max_lat}
              AND lon >= {min_lon} AND lon <= {max_lon}
        """
        
        result = self.conn.execute(query).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        
        return [dict(zip(columns, row)) for row in result]
    
    def query_features_by_location(
        self,
        table: str,
        date: str,
        lat: float,
        lon: float,
        resolution: float = 0.25
    ) -> Optional[Dict[str, Any]]:
        """
        Query features for a specific location and date.
        
        Snaps to nearest tile.
        
        Args:
            table: Table name
            date: Date string (YYYY-MM-DD)
            lat: Latitude
            lon: Longitude
            resolution: Grid resolution
        
        Returns:
            Feature dictionary or None if not found
        """
        # Snap to grid
        tile_lat = round(lat / resolution) * resolution
        tile_lon = round(lon / resolution) * resolution
        
        query = f"""
            SELECT *
            FROM {table}
            WHERE date = '{date}'
              AND ABS(lat - {tile_lat}) < {resolution / 2}
              AND ABS(lon - {tile_lon}) < {resolution / 2}
            LIMIT 1
        """
        
        result = self.conn.execute(query).fetchone()
        
        if result:
            columns = [desc[0] for desc in self.conn.description]
            return dict(zip(columns, result))
        return None
    
    def close(self):
        """Close database connection"""
        self.conn.close()
