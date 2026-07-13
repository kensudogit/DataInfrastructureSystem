# GCP reference architecture

| Layer | Service |
|-------|---------|
| Ingestion | Cloud Run / Cloud Functions |
| Orchestration | Cloud Composer (Airflow) |
| ETL | Dataflow / Dataproc |
| Landing | Cloud Storage |
| Warehouse | BigQuery |
| BI | Looker Studio |
| AI | Vertex AI |

Landing path: `gs://adinfra-landing/{media}/{date}/performance.jsonl`  
Load to BigQuery raw, transform with dbt (`profile: bigquery`).
