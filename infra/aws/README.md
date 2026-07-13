# AWS reference architecture for Ad Data Infrastructure

## Components

| Layer | Service |
|-------|---------|
| Ingestion | Lambda / ECS tasks calling collectors |
| Orchestration | MWAA (Managed Airflow) or Step Functions |
| ETL | AWS Glue / EMR (Spark) |
| Landing | S3 (`s3://adinfra-landing/`) |
| Warehouse | Amazon Redshift or Snowflake on AWS |
| BI | Amazon QuickSight |
| AI | Amazon Bedrock |

## Suggested S3 layout

```
s3://adinfra-landing/{media}/{yyyy-mm-dd}/performance.jsonl
s3://adinfra-curated/{yyyy-mm-dd}/fact_ad_performance.parquet
```

## Glue / Airflow

1. Daily DAG collects media APIs into landing bucket
2. Glue job or Spark on EMR curates parquet
3. COPY / dbt into Redshift mart schemas
4. QuickSight dataset on `mart.v_kpi_overview`
