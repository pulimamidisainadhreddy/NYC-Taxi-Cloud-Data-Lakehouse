"""Deterministic aggregation helpers for the NYC Taxi Streamlit dashboard."""

from __future__ import annotations

import pandas as pd

PAYMENT_NAMES = {
    0: "Flex Fare",
    1: "Credit Card",
    2: "Cash",
    3: "No Charge",
    4: "Dispute",
    5: "Unknown",
}

REQUIRED_COLUMNS = {
    "mart_daily_trip_metrics.csv": {
        "pickup_date", "total_trips", "total_revenue", "average_fare",
        "average_trip_distance", "average_trip_duration",
    },
    "mart_hourly_trip_metrics.csv": {
        "pickup_hour", "total_trips", "total_revenue", "average_distance", "average_duration",
    },
    "mart_payment_analysis.csv": {
        "payment_type", "total_trips", "total_revenue", "average_fare",
    },
    "mart_zone_performance.csv": {
        "pickup_location_id", "total_trips", "total_revenue", "average_fare", "average_distance",
    },
}


def validate_frame(frame: pd.DataFrame, filename: str) -> None:
    """Fail with a readable message when a report export is incomplete."""
    missing = REQUIRED_COLUMNS[filename].difference(frame.columns)
    if missing:
        raise ValueError(f"{filename} is missing columns: {', '.join(sorted(missing))}")


def weighted_average(frame: pd.DataFrame, column: str) -> float:
    """Weight aggregate averages by trip counts (never mean the means)."""
    if frame.empty:
        return 0.0
    counts = pd.to_numeric(frame["total_trips"], errors="coerce").fillna(0)
    values = pd.to_numeric(frame[column], errors="coerce")
    valid = (counts > 0) & values.notna()
    if not valid.any():
        return 0.0
    return float((counts[valid] * values[valid]).sum() / counts[valid].sum())


def summary(frame: pd.DataFrame) -> dict[str, float]:
    """Summarize totals for any grouped report export."""
    trips = int(frame["total_trips"].sum())
    revenue = float(frame["total_revenue"].sum())
    return {"trips": trips, "revenue": revenue, "fare": revenue / trips if trips else 0.0}


def date_filter(daily: pd.DataFrame, date_start, date_end) -> pd.DataFrame:
    """Apply date filter only to daily metrics, the sole date-grained export."""
    return daily.loc[
        daily["pickup_date"].dt.date.between(date_start, date_end, inclusive="both")
    ].copy()


def verify_consistency(frames: dict[str, pd.DataFrame]) -> tuple[bool, dict[str, int]]:
    """Check all four marts represent the same overall trip volume."""
    counts = {name: int(df.total_trips.sum()) for name, df in frames.items()}
    return len(set(counts.values())) == 1, counts
