{{ config(materialized='view') }}

select
    grain_key,
    report_date,
    media,
    account_id,
    account_name,
    campaign_id,
    campaign_name,
    adgroup_id,
    adgroup_name,
    ad_id,
    ad_name,
    currency,
    impressions,
    clicks,
    conversions,
    spend,
    conversion_value,
    ctr,
    cpc,
    cpm,
    cpa,
    roas,
    collected_at
from {{ source('staging', 'fact_ad_performance') }}
