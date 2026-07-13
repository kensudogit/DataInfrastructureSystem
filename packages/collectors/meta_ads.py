from __future__ import annotations

from datetime import date

from packages.collectors.base import BaseCollector
from packages.collectors.mock_data import generate_mock_records
from packages.common.schema import AdPerformanceRecord, MediaPlatform


class MetaAdsCollector(BaseCollector):
    media = MediaPlatform.META

    def fetch(self, report_date: date) -> list[AdPerformanceRecord]:
        if self._should_use_mock(
            self.settings.meta_access_token,
            self.settings.meta_ad_account_id,
        ):
            return generate_mock_records(self.media, report_date)

        raise NotImplementedError(
            "Meta Marketing API collector is not configured. "
            "Set META_ACCESS_TOKEN / META_AD_ACCOUNT_ID or keep COLLECTOR_USE_MOCK=true."
        )
