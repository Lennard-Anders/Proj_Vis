from __future__ import annotations

from datetime import datetime, timedelta
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path("/app/data")


class FireHistoryRAG:
    """Lightweight RAG helper around cached fire history CSV exports."""

    def __init__(self, pattern: str = "fire_history*.csv") -> None:
        self.pattern = pattern
        self.df: Optional[pd.DataFrame] = None
        self._load_data()

    def _load_data(self) -> None:
        """Load all matching fire history CSVs from DATA_DIR into a single DataFrame."""
        try:
            files = list(DATA_DIR.glob(self.pattern))
            if not files:
                logger.warning("No fire history CSV files found for RAG")
                self.df = None
                return

            frames: list[pd.DataFrame] = []
            for file_path in files:
                try:
                    frames.append(pd.read_csv(file_path))
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to read fire history CSV %s: %s", file_path, exc)

            if not frames:
                self.df = None
                return

            df = pd.concat(frames, ignore_index=True)

            required = {"event_id", "latitude", "longitude", "date"}
            if not required.issubset(df.columns):
                missing = required - set(df.columns)
                logger.warning("Fire history CSV is missing required columns: %s", missing)
                self.df = None
                return

            df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
            df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
            df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
            df = df.dropna(subset=["date_dt", "latitude", "longitude"])

            self.df = df
            logger.info("Loaded fire history for RAG: %d rows", len(df))
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load fire history for RAG: %s", exc)
            self.df = None

    def is_ready(self) -> bool:
        return self.df is not None and not self.df.empty

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Compute great-circle distance between two points in kilometers."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def retrieve_events(
        self,
        latitude: float,
        longitude: float,
        date_str: Optional[str] = None,
        radius_km: float = 100.0,
        days_back: int = 365,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Find historical events near a point and time window.

        - Filter by distance (radius_km).
        - Filter by time window (date - days_back to date), if date_str is provided.
        - Sort by temporal proximity and distance.
        """
        if not self.is_ready():
            return []

        df = self.df.copy()

        query_date: Optional[datetime] = None
        if date_str:
            try:
                query_date = datetime.fromisoformat(date_str)
            except Exception:  # noqa: BLE001
                logger.warning("Invalid date_str for RAG: %s", date_str)

        if query_date is not None:
            start_date = query_date - timedelta(days=days_back)
            mask = (df["date_dt"] >= start_date) & (df["date_dt"] <= query_date)
            df = df.loc[mask]

        if df.empty:
            return []

        df["distance_km"] = df.apply(
            lambda row: self._haversine_km(
                float(latitude),
                float(longitude),
                float(row["latitude"]),
                float(row["longitude"]),
            ),
            axis=1,
        )
        df = df[df["distance_km"] <= radius_km]

        if df.empty:
            return []

        if query_date is not None:
            df["time_diff_days"] = (query_date - df["date_dt"]).abs().dt.days
            df = df.sort_values(["time_diff_days", "distance_km"])
        else:
            df = df.sort_values(["distance_km", "date_dt"], ascending=[True, False])

        df = df.head(limit)

        records: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            record = row.to_dict()
            record.pop("date_dt", None)
            record.pop("distance_km", None)
            record.pop("time_diff_days", None)
            records.append(record)

        return records

    def format_events_for_llm(self, events: List[Dict[str, Any]]) -> str:
        """
        Format historical events as a concise text block for the LLM.

        Include optional weather columns when present.
        """
        if not events:
            return ""

        lines = ["Historical wildfire events near the requested location:"]
        for e in events:
            date = e.get("date")
            lat_val = e.get("latitude")
            lon_val = e.get("longitude")
            region = e.get("region")
            frp = e.get("fire_radiative_power")
            conf = e.get("confidence")
            area = e.get("area_km2")

            temp = e.get("temperature") or e.get("temperature_c")
            wind = e.get("wind_speed") or e.get("wind_speed_10m")
            rh = e.get("humidity") or e.get("rh")
            rain = e.get("rain_24h")
            prob = e.get("probability") or e.get("risk_score")

            coord_str = f"lat {lat_val}, lon {lon_val}"
            if isinstance(lat_val, (int, float)) and isinstance(lon_val, (int, float)):
                coord_str = f"lat {lat_val:.4f}, lon {lon_val:.4f}"

            line = f"- Date {date}, {coord_str}"
            if region:
                line += f", region {region}"
            if frp is not None:
                line += f", FRP {frp}"
            if conf is not None:
                line += f", confidence {conf}"
            if area is not None:
                line += f", burned area ~{area} km^2"
            if temp is not None:
                line += f", pre-fire temp ~{temp} degC"
            if wind is not None:
                line += f", wind ~{wind} m/s"
            if rh is not None:
                line += f", humidity ~{rh}%"
            if rain is not None:
                line += f", rain_24h ~{rain} mm"
            if prob is not None:
                line += f", historical fire probability ~{prob}"

            lines.append(line)

        return "\n".join(lines)


fire_history_rag = FireHistoryRAG()


def get_fire_history_context(
    latitude: float,
    longitude: float,
    date_str: Optional[str] = None,
    radius_km: float = 100.0,
    days_back: int = 365,
    limit: int = 20,
) -> str:
    """Retrieve and format historical fire data as context for LLM prompts."""
    try:
        if not fire_history_rag.is_ready():
            return ""
        events = fire_history_rag.retrieve_events(
            latitude=latitude,
            longitude=longitude,
            date_str=date_str,
            radius_km=radius_km,
            days_back=days_back,
            limit=limit,
        )
        if not events:
            return ""
        return fire_history_rag.format_events_for_llm(events)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to build fire history RAG context: %s", exc)
        return ""
