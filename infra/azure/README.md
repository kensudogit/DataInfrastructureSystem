# Azure reference architecture

| Layer | Service |
|-------|---------|
| Ingestion | Azure Functions / Container Apps |
| Orchestration | Azure Data Factory / Airflow on AKS |
| Landing | ADLS Gen2 |
| Warehouse | Synapse / Snowflake |
| BI | Power BI |
| AI | Azure OpenAI |

Map collector outputs to `abfss://landing@.../{media}/{date}/performance.jsonl`.
Use Data Factory Copy + dbt for mart builds. Connect Power BI to mart views.
