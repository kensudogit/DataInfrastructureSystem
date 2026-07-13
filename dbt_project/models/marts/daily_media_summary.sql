{{ config(materialized='table') }}

with base as (
    select * from {{ ref('stg_ad_performance') }}
)

select
    report_date,
    media,
    sum(impressions) as impressions,
    sum(clicks) as clicks,
    sum(conversions) as conversions,
    sum(spend) as spend,
    sum(conversion_value) as conversion_value,
    case when sum(impressions) = 0 then null else sum(clicks)::float / sum(impressions) end as ctr,
    case when sum(clicks) = 0 then null else sum(spend) / sum(clicks) end as cpc,
    case when sum(impressions) = 0 then null else sum(spend) / sum(impressions) * 1000 end as cpm,
    case when sum(conversions) = 0 then null else sum(spend) / sum(conversions) end as cpa,
    case when sum(spend) = 0 then null else sum(conversion_value) / sum(spend) end as roas
from base
group by 1, 2
