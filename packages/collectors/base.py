"""Base collector interface for advertising platforms."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

from packages.common.config import Settings, get_settings
from packages.common.schema import AdPerformanceRecord, MediaPlatform


class BaseCollector(ABC):
    media: MediaPlatform

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @abstractmethod
    def fetch(self, report_date: date) -> list[AdPerformanceRecord]:
        """Fetch performance records for a single report date."""

    def collect(self, report_date: date) -> Path:
        records = self.fetch(report_date)
        out_dir = self.settings.landing_dir / self.media.value / report_date.isoformat()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "performance.jsonl"
        with out_path.open("w", encoding="utf-8") as fp:
            for record in records:
                fp.write(json.dumps(record.to_flat_dict(), ensure_ascii=False, default=str))
                fp.write("\n")
        return out_path

    def _should_use_mock(self, *credential_values: str | None) -> bool:
        if self.settings.collector_use_mock:
            return True
        return not all(credential_values)
