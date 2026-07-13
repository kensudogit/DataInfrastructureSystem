"""Run collect + transform for a given date (local one-shot pipeline)."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.collectors.registry import get_all_collectors
from packages.transformers.pipeline import transform_day


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ad media collect+transform pipeline")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--load-db", action="store_true")
    args = parser.parse_args()

    report_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    for collector in get_all_collectors():
        path = collector.collect(report_date)
        print(f"collected {collector.media.value}: {path}")

    paths = transform_day(report_date)
    for name, path in paths.items():
        print(f"curated {name}: {path}")

    if args.load_db:
        from packages.transformers.pipeline import load_to_postgres

        load_to_postgres(report_date)
        print("loaded into postgres")


if __name__ == "__main__":
    main()
