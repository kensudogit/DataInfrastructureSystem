"""Shared configuration for DataInfrastructureSystem."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg2://adinfra:adinfra@localhost:5433/adinfra"
    warehouse_target: Literal["postgres", "snowflake", "bigquery", "redshift"] = "postgres"

    landing_path: str = "./data/landing"
    curated_path: str = "./data/curated"
    collector_use_mock: bool = True

    google_ads_developer_token: str | None = None
    google_ads_client_id: str | None = None
    google_ads_client_secret: str | None = None
    google_ads_refresh_token: str | None = None
    google_ads_customer_id: str | None = None

    yahoo_ads_app_id: str | None = None
    yahoo_ads_secret: str | None = None
    yahoo_ads_refresh_token: str | None = None

    meta_access_token: str | None = None
    meta_ad_account_id: str | None = None
    meta_app_id: str | None = None
    meta_app_secret: str | None = None

    x_bearer_token: str | None = None
    x_api_key: str | None = None
    x_api_secret: str | None = None
    x_access_token: str | None = None
    x_access_secret: str | None = None

    line_ads_access_key: str | None = None
    line_ads_secret_key: str | None = None

    tiktok_access_token: str | None = None
    tiktok_advertiser_id: str | None = None

    ai_provider: Literal["openai", "azure_openai", "bedrock", "vertex", "mock"] = "openai"
    openai_api_key: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    aws_bedrock_region: str = "ap-northeast-1"
    gcp_vertex_project: str | None = None
    gcp_vertex_location: str = "asia-northeast1"

    @property
    def landing_dir(self) -> Path:
        path = Path(self.landing_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def curated_dir(self) -> Path:
        path = Path(self.curated_path)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
