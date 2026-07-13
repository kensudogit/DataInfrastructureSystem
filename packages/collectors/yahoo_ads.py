from __future__ import annotations

from datetime import date

from packages.collectors.base import BaseCollector
from packages.collectors.mock_data import generate_mock_records
from packages.common.schema import AdPerformanceRecord, MediaPlatform


class YahooAdsCollector(BaseCollector):
    media = MediaPlatform.YAHOO

    def fetch(self, report_date: date) -> list[AdPerformanceRecord]:
        if self._should_use_mock(
            self.settings.yahoo_ads_app_id,
            self.settings.yahoo_ads_secret,
            self.settings.yahoo_ads_refresh_token,
        ):
            return generate_mock_records(self.media, report_date)

        raise NotImplementedError(
            "Yahoo! Ads live API collector is not configured. "
            "Set credentials or keep COLLECTOR_USE_MOCK=true."
        )
