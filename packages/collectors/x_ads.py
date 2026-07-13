from __future__ import annotations

from datetime import date

from packages.collectors.base import BaseCollector
from packages.collectors.mock_data import generate_mock_records
from packages.common.schema import AdPerformanceRecord, MediaPlatform


class XAdsCollector(BaseCollector):
    media = MediaPlatform.X

    def fetch(self, report_date: date) -> list[AdPerformanceRecord]:
        if self._should_use_mock(
            self.settings.x_bearer_token or self.settings.x_api_key,
        ):
            return generate_mock_records(self.media, report_date)

        raise NotImplementedError(
            "X Ads API collector is not configured. "
            "Set X credentials or keep COLLECTOR_USE_MOCK=true."
        )
