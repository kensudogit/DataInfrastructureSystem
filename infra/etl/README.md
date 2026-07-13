# ETL / ELT tool mapping

| Tool | Role in this package |
|------|----------------------|
| Apache Airflow | Primary orchestrator (`airflow/dags/ad_media_daily_etl.py`) |
| AWS Glue | Spark-compatible job pattern in `spark/jobs/` + `infra/aws` |
| Dataflow | GCP streaming/batch equivalent; see `infra/gcp` |
| Talend | Enterprise GUI ETL: call collector/transform CLIs as tSystem jobs |
| dbt | ELT modeling on warehouse (`dbt_project/`) |
| Pandas pipeline | Local/default transform (`packages/transformers`) |

Recommended daily flow:

1. Collect APIs -> landing
2. Transform (Pandas or Spark/Glue/Dataflow)
3. Load staging
4. dbt run -> marts
5. BI / API / AI consume marts
