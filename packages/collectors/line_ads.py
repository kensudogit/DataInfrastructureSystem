from __future__ import annotations

from datetime import date

from packages.collectors.base import BaseCollector
from packages.collectors.mock_data import generate_mock_records
from packages.common.schema import AdPerformanceRecord, MediaPlatform


class LineAdsCollector(BaseCollector):
    media = MediaPlatform.LINE

    def fetch(self, report_date: date) -> list[AdPerformanceRecord]:
        if self._should_use_mock(
            self.settings.line_ads_access_key,
            self.settings.line_ads_secret_key,
        ):
            return generate_mock_records(self.media, report_date)

        raise NotImplementedError(
            "LINE Ads API collector is not configured. "
            "Set LINE credentials or keep COLLECTOR_USE_MOCK=true."
        )
