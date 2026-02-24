from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Being Rich Assistant API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    ibkr_api_key: str = Field(default="", alias="IBKR_API_KEY")
    ibkr_api_secret: str = Field(default="", alias="IBKR_API_SECRET")
    ibkr_account_id: str = Field(default="", alias="IBKR_ACCOUNT_ID")
    ibkr_base_url: str = Field(
        default="https://www.interactivebrokers.com/api",
        alias="IBKR_BASE_URL",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
