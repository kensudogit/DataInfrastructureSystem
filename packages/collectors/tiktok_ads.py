from __future__ import annotations

from datetime import date

from packages.collectors.base import BaseCollector
from packages.collectors.mock_data import generate_mock_records
from packages.common.schema import AdPerformanceRecord, MediaPlatform


class TikTokAdsCollector(BaseCollector):
    media = MediaPlatform.TIKTOK

    def fetch(self, report_date: date) -> list[AdPerformanceRecord]:
        if self._should_use_mock(
            self.settings.tiktok_access_token,
            self.settings.tiktok_advertiser_id,
        ):
            return generate_mock_records(self.media, report_date)

        raise NotImplementedError(
            "TikTok Ads API collector is not configured. "
            "Set TIKTOK credentials or keep COLLECTOR_USE_MOCK=true."
        )
