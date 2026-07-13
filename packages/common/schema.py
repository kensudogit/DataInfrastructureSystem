"""Canonical advertising performance schema used across media platforms."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, computed_field


class MediaPlatform(str, Enum):
    GOOGLE = "google"
    YAHOO = "yahoo"
    META = "meta"
    X = "x"
    LINE = "line"
    TIKTOK = "tiktok"


class AdPerformanceRecord(BaseModel):
    """Normalized daily performance grain: account/campaign/adgroup/ad."""

    report_date: date
    media: MediaPlatform
    account_id: str
    account_name: str | None = None
    campaign_id: str
    campaign_name: str | None = None
    adgroup_id: str | None = None
    adgroup_name: str | None = None
    ad_id: str | None = None
    ad_name: str | None = None
    currency: str = "JPY"

    impressions: int = 0
    clicks: int = 0
    conversions: float = 0.0
    spend: float = 0.0
    conversion_value: float = 0.0

    raw_payload: dict[str, Any] = Field(default_factory=dict)
    collected_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ctr(self) -> float | None:
        if self.impressions <= 0:
            return None
        return self.clicks / self.impressions

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cpc(self) -> float | None:
        if self.clicks <= 0:
            return None
        return self.spend / self.clicks

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cpm(self) -> float | None:
        if self.impressions <= 0:
            return None
        return self.spend / self.impressions * 1000

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cpa(self) -> float | None:
        if self.conversions <= 0:
            return None
        return self.spend / self.conversions

    @computed_field  # type: ignore[prop-decorator]
    @property
    def roas(self) -> float | None:
        if self.spend <= 0:
            return None
        return self.conversion_value / self.spend

    def to_flat_dict(self) -> dict[str, Any]:
        data = self.model_dump(mode="json")
        data.update(
            {
                "ctr": self.ctr,
                "cpc": self.cpc,
                "cpm": self.cpm,
                "cpa": self.cpa,
                "roas": self.roas,
            }
        )
        return data


METRIC_COLUMNS = [
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

DIMENSION_COLUMNS = [
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
]
