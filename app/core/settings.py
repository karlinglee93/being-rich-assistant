from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Being Rich Assistant API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    yfinance_timeout_seconds: int = Field(default=10, alias="YFINANCE_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
