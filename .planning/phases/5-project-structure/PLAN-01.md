## Phase Goal

Establish a production-quality directory layout for the web scraping ETL pipeline with clear module boundaries separating scraping, data models, persistence, API, scheduling, and integrations.

## Files to Create

```file:pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "etl-pipeline"
version = "0.1.0"
description = "Business Process Automation — Web Scraping + Data Pipeline"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "playwright>=1.42.0",
    "sqlalchemy[asyncio]>=2.0.27",
    "asyncpg>=0.29.0",
    "alembic>=1.13.1",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.2.0",
    "httpx>=0.27.0",
    "apscheduler>=3.10.4",
    "python-telegram-bot>=21.0",
    "gspread>=6.0.0",
    "tenacity>=8.2.3",
    "structlog>=24.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.5",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "types-python-dateutil",
]

[tool.setuptools.packages.find]
where = ["src"]
include = ["etl_*"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-ra --strict-markers"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "PT", "RUF"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src"]

[[tool.mypy.overrides]]
module = ["playwright.*", "apscheduler.*", "telegram.*"]
ignore_missing_imports = true
```

```file:.env.example
# Application
APP_ENV=development
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://etl_user:etl_pass@localhost:5432/etl_db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Scraping
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT_MS=30000
SCRAPER_USER_AGENT=Mozilla/5.0 (compatible; ETLBot/0.1)

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=./secrets/google-credentials.json
GOOGLE_SHEETS_ID=

# Scheduling
SCHEDULER_ENABLED=true
SCRAPE_CRON=0 */6 * * *

# API
API_HOST=0.0.0.0
API_PORT=8000
```

```file:.gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.eggs/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
env/
ENV/

# Testing
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.mypy_cache/
.ruff_cache/
.tox/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Secrets
secrets/
*.pem
*.key
credentials.json

# Data
data/raw/
data/processed/
*.csv
*.parquet

# Logs
logs/
*.log

# Playwright
.playwright/
```

```file:README.md
# ETL Pipeline — Web Scraping + Data Pipeline

Automated ETL pipeline that scrapes business data from target websites, validates and persists it to PostgreSQL, then delivers results via CSV, Google Sheets, and Telegram.

## Stack

- **Python 3.12** — runtime
- **Playwright** — browser-based scraping (Chromium)
- **FastAPI** — async HTTP API
- **PostgreSQL + SQLAlchemy 2.0 (async) + asyncpg** — persistence
- **Pydantic v2** — data validation
- **APScheduler** — cron scheduling
- **Telegram Bot API + Google Sheets API** — delivery channels

## Project Structure

```
src/
├── etl_config/      # Settings and environment loading
├── etl_models/      # Pydantic domain models
├── etl_db/          # SQLAlchemy ORM, sessions, migrations
├── etl_scrapers/    # Playwright scrapers per source
├── etl_pipeline/    # ETL orchestration (extract → transform → load)
├── etl_api/         # FastAPI application and routes
├── etl_scheduler/   # APScheduler jobs
├── etl_delivery/    # CSV, Sheets, Telegram exporters
└── etl_common/      # Logging, exceptions, retry utilities
```

## Quick Start

```bash
# Install
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium

# Configure
cp .env.example .env  # edit values

# Database
alembic upgrade head

# Run API
uvicorn etl_api.main:app --reload

# Run scheduler
python -m etl_scheduler
```

## Testing

```bash
pytest -v
pytest --cov=src
```

## Architecture

```
┌────────────┐   ┌────────────┐   ┌──────────┐   ┌──────────┐
│  Scrapers  │──▶│ Transform  │──▶│ Database │──▶│ Delivery │
│ (Playwright)│  │ (Pydantic) │   │(Postgres)│   │CSV/Sheets│
└────────────┘   └────────────┘   └──────────┘   │ Telegram │
                                                  └──────────┘
                       ▲
                       │ cron trigger
                  ┌──────────┐
                  │Scheduler │
                  └──────────┘
```
```

```file:src/etl_config/__init__.py
"""Application configuration loaded from environment variables."""
from etl_config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
```

```file:src/etl_config/settings.py
"""Centralized settings using Pydantic v2 + pydantic-settings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://etl_user:etl_pass@localhost:5432/etl_db"
    )
    database_pool_size: int = Field(default=10, ge=1)
    database_max_overflow: int = Field(default=20, ge=0)

    # Scraping
    playwright_headless: bool = Field(default=True)
    playwright_timeout_ms: int = Field(default=30_000, ge=1000)
    scraper_user_agent: str = Field(
        default="Mozilla/5.0 (compatible; ETLBot/0.1)"
    )

    # Telegram
    telegram_bot_token: str = Field(default="")
    telegram_chat_id: str = Field(default="")

    # Google Sheets
    google_sheets_credentials_path: Path = Field(
        default=Path("./secrets/google-credentials.json")
    )
    google_sheets_id: str = Field(default="")

    # Scheduling
    scheduler_enabled: bool = Field(default=True)
    scrape_cron: str = Field(default="0 */6 * * *")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1, le=65535)

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
```

```file:src/etl_models/__init__.py
"""Pydantic domain models for validated business records."""
from etl_models.business import BusinessRecord, ScrapeJobStatus, ScrapeJobResult

__all__ = ["BusinessRecord", "ScrapeJobStatus", "ScrapeJobResult"]
```

```file:src/etl_models/business.py
"""Domain models representing scraped business records."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ScrapeJobStatus(str, Enum):
    """Lifecycle states for a scrape job."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class BusinessRecord(BaseModel):
    """A single normalized business record produced by a scraper."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        frozen=True,
        extra="forbid",
    )

    source: str = Field(min_length=1, max_length=100)
    external_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=500)
    address: str | None = Field(default=None, max_length=1000)
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    website: HttpUrl | None = None
    category: str | None = Field(default=None, max_length=200)
    raw_data: dict[str, Any] = Field(default_factory=dict)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class ScrapeJobResult(BaseModel):
    """Outcome of a single scrape execution."""

    model_config = ConfigDict(extra="forbid")

    job_id: str
    source: str
    status: ScrapeJobStatus
    records_count: int = Field(ge=0)
    started_at: datetime
    finished_at: datetime | None = None
    error_message: str | None = None
```

```file:src/etl_db/__init__.py
"""Database access layer: SQLAlchemy ORM, sessions, base."""
from etl_db.base import Base
from etl_db.session import async_session_factory, get_session, init_engine

__all__ = ["Base", "async_session_factory", "get_session", "init_engine"]
```

```file:src/etl_db/base.py
"""SQLAlchemy declarative base."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
```

```file:src/etl_db/session.py
"""Async database engine and session factory."""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from etl_config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine() -> AsyncEngine:
    """Initialize the global async engine (idempotent)."""
    global _engine, _session_factory
    if _engine is not None:
        return _engine

    settings = get_settings()
    _engine = create_async_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        echo=settings.is_development,
    )
    _session_factory = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    return _engine


def async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory, initializing if needed."""
    if _session_factory is None:
        init_engine()
    assert _session_factory is not None
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields an async session."""
    factory = async_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """Dispose of the global engine (call on shutdown)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
```

```file:src/etl_db/models/__init__.py
"""ORM entity definitions."""
from etl_db.models.business import BusinessORM
from etl_db.models.scrape_job import ScrapeJobORM

__all__ = ["BusinessORM", "ScrapeJobORM"]
```

```file:src/etl_db/models/business.py
"""SQLAlchemy ORM model for persisted business records."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from etl_db.base import Base


class BusinessORM(Base):
    """Persisted business record with source-based deduplication."""

    __tablename__ = "businesses"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    address: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    category: Mapped[str | None] = mapped_column(String(200), nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
```

```file:src/etl_db/models/scrape_job.py
"""SQLAlchemy ORM model for scrape job tracking and DLQ."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from etl_db.base import Base


class ScrapeJobORM(Base):
    """Tracks scrape job execution, retries, and dead-letter state."""

    __tablename__ = "scrape_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
```

```file:src/etl_scrapers/__init__.py
"""Web scrapers built on Playwright."""
from etl_scrapers.base import BaseScraper, ScrapedItem

__all__ = ["BaseScraper", "ScrapedItem"]
```

```file:src/etl_scrapers/base.py
"""Abstract base class for all scrapers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ScrapedItem:
    """Raw item as parsed from a webpage, pre-validation."""

    source: str
    external_id: str
    raw: dict[str, Any]


class BaseScraper(ABC):
    """Interface every source-specific scraper must implement."""

    source_name: str = ""

    def __init__(self, source_name: str) -> None:
        if not source_name:
            raise ValueError("source_name must be non-empty")
        self.source_name = source_name

    @abstractmethod
    async def scrape(self) -> list[ScrapedItem]:
        """Execute the scrape and return raw items."""
        raise NotImplementedError
```

```file:src/etl_pipeline/__init__.py
"""ETL orchestration: extract → transform → load."""
from etl_pipeline.pipeline import ETLPipeline

__all__ = ["ETLPipeline"]
```

```file:src/etl_pipeline/pipeline.py
"""Pipeline orchestrator coordinating extract, transform, and load stages."""
from __future__ import annotations

from collections.abc import Iterable

from etl_models import BusinessRecord
from etl_scrapers import BaseScraper


class ETLPipeline:
    """Coordinate a single end-to-end ETL run for one scraper."""

    def __init__(self, scraper: BaseScraper) -> None:
        self._scraper = scraper

    def transform(self, raw_items: Iterable) -> list[BusinessRecord]:
        """Validate raw items into BusinessRecord instances (stub)."""
        return []

    async def run(self) -> list[BusinessRecord]:
        """Execute extract → transform. Load handled by persistence layer."""
        raw = await self._scraper.scrape()
        return self.transform(raw)
```

```file:src/etl_api/__init__.py
"""FastAPI HTTP API."""
from etl_api.main import app

__all__ = ["app"]
```

```file:src/etl_api/main.py
"""FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from etl_db import dispose_engine, init_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    init_engine()
    try:
        yield
    finally:
        await dispose_engine()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="ETL Pipeline API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

```file:src/etl_scheduler/__init__.py
"""APScheduler-based cron job runner."""
from etl_scheduler.runner import run_scheduler

__all__ = ["run_scheduler"]
```

```file:src/etl_scheduler/runner.py
"""Scheduler entry point."""
from __future__ import annotations

import structlog

from etl_config import get_settings

logger = structlog.get_logger(__name__)


def run_scheduler() -> None:
    """Start the APScheduler instance (placeholder for Phase 5 scaffold)."""
    settings = get_settings()
    logger.info("scheduler.start", enabled=settings.scheduler_enabled, cron=settings.scrape_cron)
```

```file:src/etl_delivery/__init__.py
"""Delivery channels: CSV, Google Sheets, Telegram."""
from etl_delivery.csv_exporter import export_to_csv
from etl_delivery.sheets_exporter import export_to_sheets
from etl_delivery.telegram_exporter import export_to_telegram

__all__ = ["export_to_csv", "export_to_sheets", "export_to_telegram"]
```

```file:src/etl_delivery/csv_exporter.py
"""CSV export stub."""
from __future__ import annotations

from pathlib import Path


async def export_to_csv(records: list, output_path: Path) -> Path:
    """Persist records to a CSV file (implementation in later phase)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path
```

```file:src/etl_delivery/sheets_exporter.py
"""Google Sheets export stub."""
from __future__ import annotations


async def export_to_sheets(records: list, spreadsheet_id: str) -> None:
    """Push records into a Google Sheets spreadsheet (later phase)."""
    return None
```

```file:src/etl_delivery/telegram_exporter.py
"""Telegram delivery stub."""
from __future__ import annotations


async def export_to_telegram(records: list, chat_id: str) -> None:
    """Send a summary message via Telegram bot (later phase)."""
    return None
```

```file:src/etl_common/__init__.py
"""Shared utilities: logging, exceptions, retry helpers."""
from etl_common.logging import configure_logging, get_logger
from etl_common.exceptions import (
    ScraperError,
    ValidationError,
    DeliveryError,
)

__all__ = [
    "configure_logging",
    "get_logger",
    "ScraperError",
    "ValidationError",
    "DeliveryError",
]
```

```file:src/etl_common/logging.py
"""Structured logging configuration via structlog."""
from __future__ import annotations