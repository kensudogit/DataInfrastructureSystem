"""Daily multi-media advertising ETL DAG."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path("/opt/airflow/project")
if PROJECT_ROOT.exists() and str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _target_date(**context) -> str:
    # Use logical date (data interval start) as report date
    logical = context["data_interval_start"]
    return logical.strftime("%Y-%m-%d")


def collect_all(**context) -> str:
    from datetime import datetime as dt

    from packages.collectors.registry import get_all_collectors

    report_date = dt.strptime(_target_date(**context), "%Y-%m-%d").date()
    for collector in get_all_collectors():
        collector.collect(report_date)
    return report_date.isoformat()


def transform_and_load(**context) -> str:
    from datetime import datetime as dt

    from packages.transformers.pipeline import transform_day

    report_date = dt.strptime(_target_date(**context), "%Y-%m-%d").date()
    paths = transform_day(report_date)
    try:
        from packages.transformers.pipeline import load_to_postgres

        load_to_postgres(report_date)
    except Exception as exc:  # noqa: BLE001 - keep DAG resilient locally
        print(f"DB load skipped/failed: {exc}")
    return str(paths)


default_args = {
    "owner": "adinfra",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="ad_media_daily_etl",
    default_args=default_args,
    description="Collect and transform multi-platform ad performance",
    schedule_interval="0 6 * * *",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["ads", "etl"],
) as dag:
    collect = PythonOperator(
        task_id="collect_all_media",
        python_callable=collect_all,
        provide_context=True,
    )
    transform = PythonOperator(
        task_id="transform_and_load",
        python_callable=transform_and_load,
        provide_context=True,
    )
    collect >> transform
