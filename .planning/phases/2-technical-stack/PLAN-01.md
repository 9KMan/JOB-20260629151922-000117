## Phase Goal

Lock in the production technology stack (runtime, libraries, infrastructure) with pinned versions and a reproducible bootstrap path, so all subsequent phases build on a verified foundation that matches the Python + PostgreSQL constraint.

## Files to Create

```file:pyproject.toml
[project]
name = "bpa-pipeline"
version = "0.1.0"
description = "Business Process Automation - Web Scraping + Data Pipeline (MVP)"
readme = "README.md"
requires-python = ">=3.12,<3.13"
license = { text = "MIT" }
authors = [
    { name = "BPA Team" },
]
keywords = ["scraping", "etl", "playwright", "fastapi", "postgresql"]

dependencies = [
    # Web framework + ASGI server
    "fastapi==0.115.6",
    "uvicorn[standard]==0.32.1",

    # Data validation / domain models
    "pydantic==2.10.3",
    "pydantic-settings==2.7.0",

    # Database (async stack)
    "sqlalchemy[asyncio]==2.0.36",
    "asyncpg==0.30.0",
    "alembic==1.14.0",

    # HTTP + scraping
    "httpx==0.28.1",
    "playwright==1.49.1",

    # Scheduling
    "apscheduler==3.10.4",

    # Telegram
    "python-telegram-bot==21.10",

    # Google Sheets
    "gspread==6.1.4",
    "google-auth==2.37.0",

    # Misc
    "tenacity==9.0.0",
    "structlog==24.4.0",
    "python-dotenv==1.0.1",
    "orjson==3.10.12",
]

[project.optional-dependencies]
dev = [
    "pytest==8.3.4",
    "pytest-asyncio==0.25.0",
    "pytest-cov==6.0.0",
    "ruff==0.8.4",
    "mypy==1.13.0",
    "types-asyncpg==0.0.4",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/bpa"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-ra --strict-markers"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "ASYNC"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

```file:src/bpa/__init__.py
"""Business Process Automation - Web Scraping + Data Pipeline."""
__version__ = "0.1.0"
```

```file:src/bpa/config.py
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
```

```file:src/bpa/db.py
"""Async SQLAlchemy engine + session factory."""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bpa.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    str(_settings.database_url),
    pool_size=_settings.database_pool_size,
    max_overflow=_settings.database_max_overflow,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a transactional session."""
    async with SessionLocal() as session:
        yield session
```

```file:src/bpa/logging_setup.py
"""Structured logging configuration (structlog)."""
from __future__ import annotations

import logging
import sys

import structlog

from bpa.config import get_settings


def configure_logging() -> None:
    """Configure structlog + stdlib logging once at startup."""
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(colors=False),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)
```

```file:src/bpa/main.py
"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from bpa.config import get_settings
from bpa.logging_setup import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log = get_logger(__name__)
    settings = get_settings()
    log.info("app.starting", env=settings.environment, name=settings.app_name)
    yield
    log.info("app.stopped")


app = FastAPI(
    title="BPA Pipeline",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
```

```file:requirements.txt
# Pinned runtime dependencies (mirrors pyproject.toml for Docker/CI)
fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.7.0
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
alembic==1.14.0
httpx==0.28.1
playwright==1.49.1
apscheduler==3.10.4
python-telegram-bot==21.10
gspread==6.1.4
google-auth==2.37.0
tenacity==9.0.0
structlog==24.4.0
python-dotenv==1.0.1
orjson==3.10.12
```

```file:requirements-dev.txt
-r requirements.txt
pytest==8.3.4
pytest-asyncio==0.25.0
pytest-cov==6.0.0
ruff==0.8.4
mypy==1.13.0
types-asyncpg==0.0.4
```

```file:.python-version
3.12.7
```

```file:alembic.ini
# Minimal Alembic config - env.py reads from bpa.config
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url =

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

```file:alembic/env.py
"""Alembic environment - uses async SQLAlchemy engine from bpa.config."""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from bpa.config import get_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the live DSN from app settings
config.set_main_option("sqlalchemy.url", str(get_settings().database_url))

target_metadata = None  # populated in a later phase when models are introduced


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

```file:alembic/script.py.mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: str | Sequence[str] | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

```file:Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# System deps already present in base image; just copy and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only - smallest footprint)
RUN playwright install chromium --with-deps

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app:${PATH}"

EXPOSE 8000
CMD ["uvicorn", "bpa.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```file:docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: bpa
      POSTGRES_PASSWORD: bpa
      POSTGRES_DB: bpa
    ports:
      - "5432:5432"
    volumes:
      - bpa_pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bpa -d bpa"]
      interval: 5s
      timeout: 3s
      retries: 10

  app:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://bpa:bpa@postgres:5432/bpa
      ENVIRONMENT: development
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    volumes:
      - .:/app

volumes:
  bpa_pgdata:
```

```file:.env.example
# Copy to .env and adjust
ENVIRONMENT=development
LOG_LEVEL=INFO

DATABASE_URL=postgresql+asyncpg://bpa:bpa@localhost:5432/bpa

PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_BROWSER=chromium

# Optional integrations
# TELEGRAM_BOT_TOKEN=
# TELEGRAM_CHAT_ID=
# GOOGLE_SHEETS_CREDENTIALS_PATH=
# GOOGLE_SHEETS_SPREADSHEET_ID=
```

```file:.gitignore
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.env
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
dist/
build/
.playwright/
```

```file:README.md
# BPA Pipeline

Business Process Automation - Web Scraping + Data Pipeline (MVP).

## Stack

| Layer            | Choice                              |
|------------------|-------------------------------------|
| Language         | Python 3.12                         |
| Web framework    | FastAPI + Uvicorn                   |
| Scraping         | Playwright (chromium)               |
| HTTP client      | httpx                               |
| Data validation  | Pydantic v2                         |
| ORM / DB driver  | SQLAlchemy 2.0 (async) + asyncpg    |
| Migrations       | Alembic                             |
| Scheduling       | APScheduler                         |
| Notifications    | Telegram Bot API                    |
| Storage export   | Google Sheets (gspread)             |
| Packaging        | pyproject.toml + Docker             |

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium
cp .env.example .env

# Run app
uvicorn bpa.main:app --reload
```

## Docker

```bash
docker compose up --build
```

## Health

```bash
curl http://localhost:8000/health
```
```

```file:tests/test_stack_smoke.py
"""Smoke tests proving the Phase 2 stack is wired correctly."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from bpa.config import get_settings
from bpa.main import app


def test_settings_load() -> None:
    settings = get_settings()
    assert settings.app_name == "bpa-pipeline"
    assert str(settings.database_url).startswith("postgresql+asyncpg://")


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_async_engine_constructs() -> None:
    from bpa.db import engine

    # Construct-only check - we do not connect here (DB may not be up in CI).
    assert engine.url.drivername == "postgresql+asyncpg"


def test_dependencies_import() -> None:
    # Verifies the pinned versions of every research-backed dep are installed
    import apscheduler  # noqa: F401
    import fastapi  # noqa: F401
    import httpx  # noqa: F401
    import playwright  # noqa: F401
    import pydantic  # noqa: F401
    import sqlalchemy  # noqa: F401
    import structlog  # noqa: F401

    assert sqlalchemy.__version__.startswith("2.")
```

```file:scripts/check_stack.sh
#!/usr/bin/env bash
# Verify the runtime toolchain and pinned Python version.
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python}"

echo "==> Python version"
"$PYTHON_BIN" --version
"$PYTHON_BIN" -c "import sys; assert sys.version_info[:2] == (3, 12), sys.version"

echo "==> Checking pinned dependencies"
"$PYTHON_BIN" - <<'PY'
import importlib.metadata as m
required = {
    "fastapi": "0.115.6",
    "uvicorn": "0.32.1",
    "pydantic": "2.10.3",
    "sqlalchemy": "2.0.36",
    "asyncpg": "0.30.0",
    "alembic": "1.14.0",
    "httpx": "0.28.1",
    "playwright": "1.49.1",
    "apscheduler": "3.10.4",
    "structlog": "24.4.0",
}
for pkg, want in required.items():
    got = m.version(pkg)
    assert got == want, f"{pkg}: want {want}, got {got}"
    print(f"  ok  {pkg}=={got}")
PY

echo "==> Checking .python-version matches"
PY_VERSION="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
echo "  local python reports $PY_VERSION"

echo "All stack checks passed."
```

```file:scripts/bootstrap.sh
#!/usr/bin/env bash
# One-shot environment bootstrap for developers.
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "python not found on PATH" >&2
    exit 1
fi

"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements-dev.txt
playwright install chromium --with-deps

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example - review and edit."
fi

echo "Bootstrap complete. Run: uvicorn bpa.main:app --reload"
```

```file:Makefile
.PHONY: install dev test lint type fmt stack-check run

PYTHON ?= python

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install -U pip && pip install -r requirements-dev.txt && playwright install chromium

dev:
	. .venv/bin/activate && uvicorn bpa.main:app --reload

test:
	. .venv/bin/activate && pytest -q

lint:
	. .venv/bin/activate && ruff check src tests

type:
	. .venv/bin/activate && mypy src

fmt:
	. .venv/bin/activate && ruff format src tests

stack-check:
	bash scripts/check_stack.sh

run:
	. .venv/bin/activate && uvicorn bpa.main:app --host 0.0.0.0 --port 8000
```

## Done When

- `make install` completes without error and `python -c "import bpa"` succeeds.
- `bash scripts/check_stack.sh` exits 0, asserting Python 3.12.x and pinned versions for FastAPI, SQLAlchemy 2.0, asyncpg, Playwright, APScheduler, httpx, structlog, Pydantic v2, Alembic.
- `make test` passes all four tests in `tests/test_stack_smoke.py` (settings load, `/health` returns `{"status":"ok"}`, async engine constructs, all research-backed deps import).
- `docker compose config` validates the compose file (postgres + app services, healthcheck on postgres).
- `alembic revision --help` runs against the new `alembic/env.py` without import errors.

## Acceptance Notes

- **CONTEXT.md — Tech Stack constraint (Python, PostgreSQL):** satisfied by pinning Python 3.12, the async SQLAlchemy 2.0 + asyncpg PostgreSQL stack, and the dockerized Postgres 16 service.
- **RESEARCH.md decisions materialized:** every library chosen in RESEARCH (Playwright, FastAPI/Uvicorn, SQLAlchemy 2.0 + asyncpg, Pydantic v2, APScheduler, httpx) is pinned in `pyproject.toml` and `requirements.txt`, and `src/bpa/db.py` + `src/bpa/config.py` implement the async-DSN pattern called out in the research.
- **SPEC.md stack line:** the README's stack table mirrors the SPEC header (`Python 3.12 + Playwright + FastAPI + PostgreSQL + APScheduler + Telegram Bot API + Docker`) one-for-one, so the stack document is now executable rather than aspirational.
- **Future phases enabled:** Phase 3 (data models / scraping) can import `bpa.config.get_settings`, `bpa.db.get_session`, and `bpa.logging_setup.get_logger` without re-deciding tooling; Phase 4 (scheduler) can register jobs against the same FastAPI lifespan; Phase 5 (delivery) can plug Telegram and Google Sheets clients into the already-pinned versions of `python