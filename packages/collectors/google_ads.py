from __future__ import annotations

from datetime import date

from packages.collectors.base import BaseCollector
from packages.collectors.mock_data import generate_mock_records
from packages.common.schema import AdPerformanceRecord, MediaPlatform


class GoogleAdsCollector(BaseCollector):
    media = MediaPlatform.GOOGLE

    def fetch(self, report_date: date) -> list[AdPerformanceRecord]:
        if self._should_use_mock(
            self.settings.google_ads_developer_token,
            self.settings.google_ads_refresh_token,
            self.settings.google_ads_customer_id,
        ):
            return generate_mock_records(self.media, report_date)

        # Placeholder for Google Ads API (google-ads library) integration.
        # Implement searchStream with customer_id + GAQL metrics query.
        raise NotImplementedError(
            "Google Ads live API collector is not configured. "
            "Set credentials and implement google-ads client, or keep COLLECTOR_USE_MOCK=true."
        )
