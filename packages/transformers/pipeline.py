"""Transform landing JSONL into curated parquet / mart aggregates."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from packages.common.config import Settings, get_settings
from packages.common.schema import DIMENSION_COLUMNS, METRIC_COLUMNS


def _grain_key(row: pd.Series) -> str:
    return "|".join(
        [
            str(row.get("report_date", "")),
            str(row.get("media", "")),
            str(row.get("account_id", "")),
            str(row.get("campaign_id", "")),
            str(row.get("adgroup_id") or ""),
            str(row.get("ad_id") or ""),
        ]
    )


def load_landing(report_date: date, settings: Settings | None = None) -> pd.DataFrame:
    cfg = settings or get_settings()
    root = cfg.landing_dir
    frames: list[pd.DataFrame] = []

    for media_dir in root.iterdir() if root.exists() else []:
        day_file = media_dir / report_date.isoformat() / "performance.jsonl"
        if not day_file.exists():
            continue
        rows = []
        with day_file.open(encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        if rows:
            frames.append(pd.DataFrame(rows))

    if not frames:
        return pd.DataFrame(columns=DIMENSION_COLUMNS + METRIC_COLUMNS)

    df = pd.concat(frames, ignore_index=True)
    df["report_date"] = pd.to_datetime(df["report_date"]).dt.date.astype(str)
    df["grain_key"] = df.apply(_grain_key, axis=1)
    return df


def build_daily_media_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    grouped = (
        df.groupby(["report_date", "media"], as_index=False)
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            spend=("spend", "sum"),
            conversion_value=("conversion_value", "sum"),
        )
    )
    grouped["ctr"] = grouped.apply(
        lambda r: (r["clicks"] / r["impressions"]) if r["impressions"] else None,
        axis=1,
    )
    grouped["cpc"] = grouped.apply(
        lambda r: (r["spend"] / r["clicks"]) if r["clicks"] else None,
        axis=1,
    )
    grouped["cpm"] = grouped.apply(
        lambda r: (r["spend"] / r["impressions"] * 1000) if r["impressions"] else None,
        axis=1,
    )
    grouped["cpa"] = grouped.apply(
        lambda r: (r["spend"] / r["conversions"]) if r["conversions"] else None,
        axis=1,
    )
    grouped["roas"] = grouped.apply(
        lambda r: (r["conversion_value"] / r["spend"]) if r["spend"] else None,
        axis=1,
    )
    return grouped


def build_campaign_performance(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    grouped = (
        df.groupby(
            ["report_date", "media", "account_id", "campaign_id", "campaign_name"],
            as_index=False,
            dropna=False,
        )
        .agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            spend=("spend", "sum"),
            conversion_value=("conversion_value", "sum"),
        )
    )
    grouped["ctr"] = grouped.apply(
        lambda r: (r["clicks"] / r["impressions"]) if r["impressions"] else None,
        axis=1,
    )
    grouped["cpc"] = grouped.apply(
        lambda r: (r["spend"] / r["clicks"]) if r["clicks"] else None,
        axis=1,
    )
    grouped["cpm"] = grouped.apply(
        lambda r: (r["spend"] / r["impressions"] * 1000) if r["impressions"] else None,
        axis=1,
    )
    grouped["cpa"] = grouped.apply(
        lambda r: (r["spend"] / r["conversions"]) if r["conversions"] else None,
        axis=1,
    )
    grouped["roas"] = grouped.apply(
        lambda r: (r["conversion_value"] / r["spend"]) if r["spend"] else None,
        axis=1,
    )
    return grouped


def transform_day(report_date: date, settings: Settings | None = None) -> dict[str, Path]:
    cfg = settings or get_settings()
    df = load_landing(report_date, cfg)
    out_root = cfg.curated_dir / report_date.isoformat()
    out_root.mkdir(parents=True, exist_ok=True)

    fact_path = out_root / "fact_ad_performance.parquet"
    daily_path = out_root / "daily_media_summary.parquet"
    campaign_path = out_root / "campaign_performance.parquet"

    df.to_parquet(fact_path, index=False)
    build_daily_media_summary(df).to_parquet(daily_path, index=False)
    build_campaign_performance(df).to_parquet(campaign_path, index=False)

    return {
        "fact": fact_path,
        "daily": daily_path,
        "campaign": campaign_path,
    }


def load_to_postgres(report_date: date, settings: Settings | None = None) -> None:
    """Optional load curated parquet into PostgreSQL mart/staging tables."""
    from sqlalchemy import create_engine, text

    cfg = settings or get_settings()
    paths = transform_day(report_date, cfg)
    engine = create_engine(cfg.database_url)

    fact = pd.read_parquet(paths["fact"])
    daily = pd.read_parquet(paths["daily"])
    campaign = pd.read_parquet(paths["campaign"])

    fact_cols = [
        "grain_key",
        "report_date",
        "media",
        "account_id",
        "account_name",
        "campaign_id",
        "campaign_name",
        "adgroup_id",
        "adgroup_name",
        "ad_id",
        "ad_name",
        "currency",
        "impressions",
        "clicks",
        "conversions",
        "spend",
        "conversion_value",
        "ctr",
        "cpc",
        "cpm",
        "cpa",
        "roas",
    ]
    daily_cols = [
        "report_date",
        "media",
        "impressions",
        "clicks",
        "conversions",
        "spend",
        "conversion_value",
        "ctr",
        "cpc",
        "cpm",
        "cpa",
        "roas",
    ]
    campaign_cols = [
        "report_date",
        "media",
        "account_id",
        "campaign_id",
        "campaign_name",
        "impressions",
        "clicks",
        "conversions",
        "spend",
        "conversion_value",
        "ctr",
        "cpc",
        "cpm",
        "cpa",
        "roas",
    ]

    if not fact.empty:
        fact = fact[[c for c in fact_cols if c in fact.columns]]
    if not daily.empty:
        daily = daily[[c for c in daily_cols if c in daily.columns]]
    if not campaign.empty:
        campaign = campaign[[c for c in campaign_cols if c in campaign.columns]]

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM staging.fact_ad_performance WHERE report_date = :d"),
            {"d": report_date.isoformat()},
        )
        conn.execute(
            text("DELETE FROM mart.daily_media_summary WHERE report_date = :d"),
            {"d": report_date.isoformat()},
        )
        conn.execute(
            text("DELETE FROM mart.campaign_performance WHERE report_date = :d"),
            {"d": report_date.isoformat()},
        )

    if not fact.empty:
        fact.to_sql(
            "fact_ad_performance",
            engine,
            schema="staging",
            if_exists="append",
            index=False,
            method="multi",
        )
    if not daily.empty:
        daily.to_sql(
            "daily_media_summary",
            engine,
            schema="mart",
            if_exists="append",
            index=False,
            method="multi",
        )
    if not campaign.empty:
        campaign.to_sql(
            "campaign_performance",
            engine,
            schema="mart",
            if_exists="append",
            index=False,
            method="multi",
        )
