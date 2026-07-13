"""Mock performance generator for local development."""
from __future__ import annotations

import hashlib
import random
from datetime import date

from packages.common.schema import AdPerformanceRecord, MediaPlatform


def generate_mock_records(
    media: MediaPlatform,
    report_date: date,
    n_campaigns: int = 3,
    seed: int | None = None,
) -> list[AdPerformanceRecord]:
    seed_value = seed if seed is not None else int(
        hashlib.md5(f"{media.value}:{report_date.isoformat()}".encode()).hexdigest()[:8],
        16,
    )
    rng = random.Random(seed_value)
    records: list[AdPerformanceRecord] = []

    for i in range(1, n_campaigns + 1):
        impressions = rng.randint(5_000, 120_000)
        clicks = max(1, int(impressions * rng.uniform(0.005, 0.04)))
        conversions = round(clicks * rng.uniform(0.02, 0.15), 2)
        spend = round(clicks * rng.uniform(40, 350), 2)
        conversion_value = round(conversions * rng.uniform(2_000, 12_000), 2)

        records.append(
            AdPerformanceRecord(
                report_date=report_date,
                media=media,
                account_id=f"{media.value}-acct-001",
                account_name=f"{media.value.upper()} Demo Account",
                campaign_id=f"{media.value}-cmp-{i:03d}",
                campaign_name=f"{media.value.upper()} Campaign {i}",
                adgroup_id=f"{media.value}-ag-{i:03d}",
                adgroup_name=f"AdGroup {i}",
                ad_id=f"{media.value}-ad-{i:03d}",
                ad_name=f"Creative {i}",
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                spend=spend,
                conversion_value=conversion_value,
                raw_payload={"source": "mock", "seed": seed_value},
            )
        )
    return records
