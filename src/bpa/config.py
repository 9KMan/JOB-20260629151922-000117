"""Application settings loaded from environment variables and .env file."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Top-level runtime settings.

    Values are populated from environment variables (or a .env file in the
    project root). All fields have sensible defaults so the application can
    boot in development without any external configuration.
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = Field(default="BPA Pipeline")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # --- Database ---
    database_url: str = Field(
        default="postgresql+asyncpg://bpa:bpa@localhost:5432/bpa"
    )
    database_pool_size: int = Field(default=5)
    database_max_overflow: int = Field(default=10)
    database_echo: bool = Field(default=False)

    # --- Scraper defaults ---
    scraper_default_timeout_ms: int = Field(default=20_000)
    scraper_default_user_agent: str = Field(
        default="Mozilla/5.0 (compatible; BPA-Pipeline/0.1; +https://example.com/bot)"
    )
    scraper_max_concurrency: int = Field(default=4)

    # --- Retry ---
    retry_max_attempts: int = Field(default=3)
    retry_initial_wait_seconds: float = Field(default=1.0)
    retry_max_wait_seconds: float = Field(default=10.0)

    # --- Scheduler ---
    scheduler_default_cron: str = Field(default="0 9 * * *")
    scheduler_timezone: str = Field(default="UTC")

    # --- Outputs ---
    csv_output_dir: str = Field(default="./exports")

    # --- Telegram (optional) ---
    telegram_bot_token: str | None = Field(default=None)
    telegram_chat_id: str | None = Field(default=None)

    # --- Google Sheets (optional) ---
    google_sheets_credentials_path: str | None = Field(default=None)
    google_sheets_spreadsheet_id: str | None = Field(default=None)

    # --- DLQ ---
    dlq_alert_after_failures: int = Field(default=3)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Using lru_cache avoids re-parsing environment variables on every access,
    while still allowing tests to override DATABASE_URL via os.environ before
    the first call.
    """
    return Settings()


def reset_settings_cache() -> None:
    """Clear the cached settings so the next get_settings() reads fresh env."""
    get_settings.cache_clear()
    # Force re-evaluation of derived paths
    os.environ.setdefault("PYTHONPATH", str(PROJECT_ROOT / "src"))