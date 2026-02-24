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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Load environment from both .env and .env.local (local overrides)
def _load_env_files():
    """Load environment variables from .env and .env.local files."""
    from pathlib import Path

    from dotenv import load_dotenv

    # Load .env first (public config)
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file, override=False)

    # Load .env.local second (local secrets override)
    env_local_file = Path(".env.local")
    if env_local_file.exists():
        load_dotenv(env_local_file, override=True)


# Load env files before creating settings instance
_load_env_files()

settings = Settings()
