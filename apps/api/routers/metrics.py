from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from packages.common.config import get_settings
from packages.common.db import (
    fetch_campaign_performance,
    fetch_daily_media_summary,
    fetch_media_master,
    postgres_available,
)

router = APIRouter(tags=["metrics"])


def _read_curated(report_date: date, name: str) -> pd.DataFrame:
    settings = get_settings()
    path = Path(settings.curated_path) / report_date.isoformat() / f"{name}.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def _merge_range(start: date, end: date, name: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    current = start
    while current <= end:
        df = _read_curated(current, name)
        if not df.empty:
            frames.append(df)
        current = date.fromordinal(current.toordinal() + 1)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _load_daily(start: date, end: date, media: str | None) -> tuple[pd.DataFrame, str]:
    if postgres_available():
        df = fetch_daily_media_summary(start, end, media)
        if not df.empty:
            return df, "postgres"
    daily = _merge_range(start, end, "daily_media_summary")
    if media and not daily.empty:
        daily = daily[daily["media"] == media]
    return daily, "parquet"


def _load_campaigns(start: date, end: date, media: str | None) -> tuple[pd.DataFrame, str]:
    if postgres_available():
        df = fetch_campaign_performance(start, end, media)
        if not df.empty:
            return df, "postgres"
    campaign = _merge_range(start, end, "campaign_performance")
    if media and not campaign.empty:
        campaign = campaign[campaign["media"] == media]
    return campaign, "parquet"


def _totals(daily: pd.DataFrame) -> dict[str, Any]:
    if daily.empty:
        return {}
    totals = {
        "impressions": int(daily["impressions"].sum()),
        "clicks": int(daily["clicks"].sum()),
        "conversions": float(daily["conversions"].sum()),
        "spend": float(daily["spend"].sum()),
        "conversion_value": float(daily["conversion_value"].sum()),
    }
    spend = totals["spend"]
    impressions = totals["impressions"]
    clicks = totals["clicks"]
    conversions = totals["conversions"]
    totals["ctr"] = (clicks / impressions) if impressions else None
    totals["cpc"] = (spend / clicks) if clicks else None
    totals["cpm"] = (spend / impressions * 1000) if impressions else None
    totals["cpa"] = (spend / conversions) if conversions else None
    totals["roas"] = (totals["conversion_value"] / spend) if spend else None
    return totals


@router.get("/metrics")
def get_metrics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    media: str | None = Query(None, description="Filter by media code"),
) -> dict[str, Any]:
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")

    daily, source = _load_daily(start_date, end_date, media)
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "source": source,
        "rows": daily.to_dict(orient="records") if not daily.empty else [],
        "totals": _totals(daily),
    }


@router.get("/campaigns")
def get_campaigns(
    start_date: date = Query(...),
    end_date: date = Query(...),
    media: str | None = None,
) -> dict[str, Any]:
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    campaign, source = _load_campaigns(start_date, end_date, media)
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "source": source,
        "rows": campaign.to_dict(orient="records") if not campaign.empty else [],
    }


@router.get("/media")
def list_media() -> dict[str, Any]:
    return {
        "source": "postgres" if postgres_available() else "static",
        "rows": fetch_media_master(),
    }
