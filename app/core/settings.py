from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Being Rich Assistant API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    frontend_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="FRONTEND_ORIGINS",
    )
    alpha_vantage_api_key: str = Field(default="", alias="ALPHA_VANTAGE_API_KEY")
    alpha_vantage_base_url: str = Field(
        default="https://www.alphavantage.co/query",
        alias="ALPHA_VANTAGE_BASE_URL",
    )
    alpha_vantage_verify_ssl: bool = Field(default=True, alias="ALPHA_VANTAGE_VERIFY_SSL")
    alpha_vantage_allow_insecure_ssl_fallback: bool = Field(
        default=True,
        alias="ALPHA_VANTAGE_ALLOW_INSECURE_SSL_FALLBACK",
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
