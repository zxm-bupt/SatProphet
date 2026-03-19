"""Application settings module."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = Field(default="SatProphet", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    database_url: str = Field(
        default="postgresql+psycopg://satprophet:satprophet@localhost:5432/satprophet",
        alias="DATABASE_URL",
    )
    spacetrack_id: str = Field(default="", alias="SPACETRACK_ID")
    spacetrack_password: str = Field(default="", alias="SPACETRACK_PASSWORD")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    ingest_interval_minutes: int = Field(default=15, alias="INGEST_INTERVAL_MINUTES")
    enable_scheduler: bool = Field(default=True, alias="ENABLE_SCHEDULER")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
