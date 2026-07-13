"""PostgreSQL access helpers for API and loaders."""
from __future__ import annotations

from datetime import date
from functools import lru_cache
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from packages.common.config import get_settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 3},
    )


def postgres_available() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def fetch_daily_media_summary(
    start_date: date,
    end_date: date,
    media: str | None = None,
) -> pd.DataFrame:
    sql = """
        SELECT
            report_date::text AS report_date,
            media,
            impressions,
            clicks,
            conversions,
            spend,
            conversion_value,
            ctr, cpc, cpm, cpa, roas
        FROM mart.daily_media_summary
        WHERE report_date BETWEEN :start_date AND :end_date
    """
    params: dict[str, Any] = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    if media:
        sql += " AND media = :media"
        params["media"] = media
    sql += " ORDER BY report_date, media"
    return pd.read_sql(text(sql), get_engine(), params=params)


def fetch_campaign_performance(
    start_date: date,
    end_date: date,
    media: str | None = None,
) -> pd.DataFrame:
    sql = """
        SELECT
            report_date::text AS report_date,
            media,
            account_id,
            campaign_id,
            campaign_name,
            impressions,
            clicks,
            conversions,
            spend,
            conversion_value,
            ctr, cpc, cpm, cpa, roas
        FROM mart.campaign_performance
        WHERE report_date BETWEEN :start_date AND :end_date
    """
    params: dict[str, Any] = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    if media:
        sql += " AND media = :media"
        params["media"] = media
    sql += " ORDER BY spend DESC"
    return pd.read_sql(text(sql), get_engine(), params=params)


def fetch_media_master() -> list[dict[str, Any]]:
    sql = """
        SELECT media_code, media_name, is_active
        FROM mart.dim_media
        WHERE is_active = TRUE
        ORDER BY media_code
    """
    try:
        df = pd.read_sql(text(sql), get_engine())
        return df.to_dict(orient="records")
    except Exception:
        return [
            {"media_code": m, "media_name": m, "is_active": True}
            for m in ("google", "yahoo", "meta", "x", "line", "tiktok")
        ]
