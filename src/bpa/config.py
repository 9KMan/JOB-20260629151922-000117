cat > src/bpa/config.py << 'EOF'
"""Application configuration loaded from environment variables.

Single source of truth for runtime settings. Uses pydantic-settings so
values are validated at startup and importable as a typed object.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core
    app_name: str = "bpa-pipeline"
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # PostgreSQL (async DSN - asyncpg driver)
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://bpa:bpa@localhost:5432/bpa"
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Scheduler
    scheduler_timezone: str = "UTC"

    # Playwright
    playwright_headless: bool = True
    playwright_browser: str = "chromium"

    # Telegram (optional - notifications are best-effort)
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # Google Sheets (optional)
    google_sheets_credentials_path: Path | None = None
    google_sheets_spreadsheet_id: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
EOF
