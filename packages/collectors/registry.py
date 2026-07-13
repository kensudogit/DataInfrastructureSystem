from __future__ import annotations

from packages.collectors.base import BaseCollector
from packages.collectors.google_ads import GoogleAdsCollector
from packages.collectors.line_ads import LineAdsCollector
from packages.collectors.meta_ads import MetaAdsCollector
from packages.collectors.tiktok_ads import TikTokAdsCollector
from packages.collectors.x_ads import XAdsCollector
from packages.collectors.yahoo_ads import YahooAdsCollector
from packages.common.config import Settings, get_settings
from packages.common.schema import MediaPlatform

COLLECTOR_REGISTRY: dict[MediaPlatform, type[BaseCollector]] = {
    MediaPlatform.GOOGLE: GoogleAdsCollector,
    MediaPlatform.YAHOO: YahooAdsCollector,
    MediaPlatform.META: MetaAdsCollector,
    MediaPlatform.X: XAdsCollector,
    MediaPlatform.LINE: LineAdsCollector,
    MediaPlatform.TIKTOK: TikTokAdsCollector,
}


def get_collector(media: MediaPlatform, settings: Settings | None = None) -> BaseCollector:
    cls = COLLECTOR_REGISTRY[media]
    return cls(settings or get_settings())


def get_all_collectors(settings: Settings | None = None) -> list[BaseCollector]:
    cfg = settings or get_settings()
    return [cls(cfg) for cls in COLLECTOR_REGISTRY.values()]
