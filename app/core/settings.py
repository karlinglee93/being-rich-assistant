from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Being Rich Assistant API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    ibkr_timeout_seconds: int = Field(default=10, alias="IBKR_TIMEOUT_SECONDS")
    ibkr_host: str = Field(default="127.0.0.1", alias="IBKR_HOST")
    ibkr_port: int = Field(default=7497, alias="IBKR_PORT")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
