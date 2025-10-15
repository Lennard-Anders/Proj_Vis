from __future__ import annotations

from pathlib import Path
from typing import Any


class DuckDBClient:
    """Minimal stub that mimics a DuckDB query interface."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def query(self, sql: str, *params: Any) -> list[dict[str, Any]]:
        return [
            {"tile_id": 1, "value": 0.23, "sql": sql, "params": params},
        ]
