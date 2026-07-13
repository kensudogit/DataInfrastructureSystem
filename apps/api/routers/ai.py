from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from packages.ai_optimizer import optimize_budget
from packages.common.config import get_settings
from packages.common.db import fetch_campaign_performance, postgres_available

router = APIRouter(tags=["ai"])


class OptimizeRequest(BaseModel):
    start_date: date
    end_date: date
    total_budget: float = Field(..., gt=0, description="Total budget in JPY")
    media: str | None = None


def _load_campaigns(start: date, end: date, media: str | None) -> pd.DataFrame:
    if postgres_available():
        df = fetch_campaign_performance(start, end, media)
        if not df.empty:
            return df

    settings = get_settings()
    frames: list[pd.DataFrame] = []
    current = start
    while current <= end:
        path = Path(settings.curated_path) / current.isoformat() / "campaign_performance.parquet"
        if path.exists():
            frames.append(pd.read_parquet(path))
        current = date.fromordinal(current.toordinal() + 1)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    if media:
        df = df[df["media"] == media]
    return df


@router.post("/ai/optimize")
def optimize(req: OptimizeRequest) -> dict[str, Any]:
    if req.end_date < req.start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    df = _load_campaigns(req.start_date, req.end_date, req.media)
    result = optimize_budget(df, req.total_budget)
    return {
        "start_date": req.start_date.isoformat(),
        "end_date": req.end_date.isoformat(),
        "total_budget": req.total_budget,
        "data_source": "postgres" if postgres_available() and not df.empty else "parquet",
        **result,
    }
