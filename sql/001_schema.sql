-- DataInfrastructureSystem core schema (PostgreSQL / Redshift compatible)
-- Layers: raw -> staging -> mart

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;

-- Raw landing table (JSON payload preserved)
CREATE TABLE IF NOT EXISTS raw.ad_performance_raw (
    id              BIGSERIAL PRIMARY KEY,
    media           VARCHAR(32)  NOT NULL,
    report_date     DATE         NOT NULL,
    account_id      VARCHAR(128) NOT NULL,
    payload         JSONB        NOT NULL,
    collected_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    source_file     TEXT
);

CREATE INDEX IF NOT EXISTS idx_raw_ad_perf_media_date
    ON raw.ad_performance_raw (media, report_date);

-- Staging normalized fact
CREATE TABLE IF NOT EXISTS staging.fact_ad_performance (
    grain_key           TEXT         PRIMARY KEY,
    report_date         DATE         NOT NULL,
    media               VARCHAR(32)  NOT NULL,
    account_id          VARCHAR(128) NOT NULL,
    account_name        TEXT,
    campaign_id         VARCHAR(128) NOT NULL,
    campaign_name       TEXT,
    adgroup_id          VARCHAR(128),
    adgroup_name        TEXT,
    ad_id               VARCHAR(128),
    ad_name             TEXT,
    currency            CHAR(3)      NOT NULL DEFAULT 'JPY',
    impressions         BIGINT       NOT NULL DEFAULT 0,
    clicks              BIGINT       NOT NULL DEFAULT 0,
    conversions         DOUBLE PRECISION NOT NULL DEFAULT 0,
    spend               DOUBLE PRECISION NOT NULL DEFAULT 0,
    conversion_value    DOUBLE PRECISION NOT NULL DEFAULT 0,
    ctr                 DOUBLE PRECISION,
    cpc                 DOUBLE PRECISION,
    cpm                 DOUBLE PRECISION,
    cpa                 DOUBLE PRECISION,
    roas                DOUBLE PRECISION,
    collected_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stg_fact_date_media
    ON staging.fact_ad_performance (report_date, media);

-- Mart: daily media summary for BI / API
CREATE TABLE IF NOT EXISTS mart.daily_media_summary (
    report_date         DATE         NOT NULL,
    media               VARCHAR(32)  NOT NULL,
    impressions         BIGINT       NOT NULL DEFAULT 0,
    clicks              BIGINT       NOT NULL DEFAULT 0,
    conversions         DOUBLE PRECISION NOT NULL DEFAULT 0,
    spend               DOUBLE PRECISION NOT NULL DEFAULT 0,
    conversion_value    DOUBLE PRECISION NOT NULL DEFAULT 0,
    ctr                 DOUBLE PRECISION,
    cpc                 DOUBLE PRECISION,
    cpm                 DOUBLE PRECISION,
    cpa                 DOUBLE PRECISION,
    roas                DOUBLE PRECISION,
    PRIMARY KEY (report_date, media)
);

-- Mart: campaign performance
CREATE TABLE IF NOT EXISTS mart.campaign_performance (
    report_date         DATE         NOT NULL,
    media               VARCHAR(32)  NOT NULL,
    account_id          VARCHAR(128) NOT NULL,
    campaign_id         VARCHAR(128) NOT NULL,
    campaign_name       TEXT,
    impressions         BIGINT       NOT NULL DEFAULT 0,
    clicks              BIGINT       NOT NULL DEFAULT 0,
    conversions         DOUBLE PRECISION NOT NULL DEFAULT 0,
    spend               DOUBLE PRECISION NOT NULL DEFAULT 0,
    conversion_value    DOUBLE PRECISION NOT NULL DEFAULT 0,
    ctr                 DOUBLE PRECISION,
    cpc                 DOUBLE PRECISION,
    cpm                 DOUBLE PRECISION,
    cpa                 DOUBLE PRECISION,
    roas                DOUBLE PRECISION,
    PRIMARY KEY (report_date, media, account_id, campaign_id)
);

-- Dimension: media master
CREATE TABLE IF NOT EXISTS mart.dim_media (
    media_code      VARCHAR(32) PRIMARY KEY,
    media_name      TEXT NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO mart.dim_media (media_code, media_name) VALUES
    ('google', 'Google Ads'),
    ('yahoo', 'Yahoo! Ads'),
    ('meta', 'Meta Ads (Facebook/Instagram)'),
    ('x', 'X Ads'),
    ('line', 'LINE Ads'),
    ('tiktok', 'TikTok Ads')
ON CONFLICT (media_code) DO NOTHING;

-- Helpful BI views
CREATE OR REPLACE VIEW mart.v_kpi_overview AS
SELECT
    report_date,
    media,
    impressions,
    clicks,
    conversions,
    spend,
    conversion_value,
    ctr,
    cpc,
    cpm,
    cpa,
    roas
FROM mart.daily_media_summary
ORDER BY report_date DESC, media;
