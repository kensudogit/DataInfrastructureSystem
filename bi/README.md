# BI connections

Curated marts are designed for BI tools:

- `mart.daily_media_summary`
- `mart.campaign_performance`
- `mart.v_kpi_overview`

## Tableau / Power BI

Connect via PostgreSQL (local) or warehouse connector (Snowflake / BigQuery / Redshift).
Recommended starter dashboard:

1. Spend / CV / ROAS trend by day
2. Media mix (stacked bar)
3. Campaign ranking by CPA / ROAS

## Looker Studio

Use BigQuery connector on `daily_media_summary` model, or PostgreSQL community connector for local demos.

## Amazon QuickSight

Point SPICE dataset at Redshift/PostgreSQL `mart.v_kpi_overview`.
