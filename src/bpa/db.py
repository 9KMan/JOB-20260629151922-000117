"""Async SQLAlchemy engine and session factory.

The engine is constructed from the configured DATABASE_URL. For SQLite URLs
used in tests, we set `connect_args={"check_same_thread": False}` so the
connection can be used across event loops (Bug 184).
"""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bpa.config import get_settings


def _build_connect_args(url: str) -> dict:
    """Return driver-specific connect_args for the given URL.

    SQLite needs `check_same_thread=False` so the same connection can service
    requests from different threads (FastAPI / pytest-asyncio behaviour).
    PostgreSQL via asyncpg does not need extra args.
    """
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _normalize_database_url(url: str) -> str:
    """Bug 197 fix (2026-06-30): ensure SQLite uses the aiosqlite async driver.

    SQLAlchemy's `create_async_engine` requires an async driver (sqlite+aiosqlite,
    postgresql+asyncpg, etc.). Without the explicit `+aiosqlite` suffix, the
    engine fails to create with `InvalidRequestError: ... is not async`.

    For `sqlite:///./test.db` we convert to `sqlite+aiosqlite:///./test.db`.
    For PostgreSQL URLs (`postgresql+asyncpg://...` or `postgresql://...`) we
    add `+asyncpg` if missing.
    """
    if url.startswith("sqlite://") and "+aiosqlite" not in url:
        return "sqlite+aiosqlite:///" + url[len("sqlite://"):]
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return "postgresql+asyncpg://" + url[len("postgresql://"):]
    return url


# Bug 197 fix (2026-06-30): normalize the URL to use the async driver BEFORE
# creating the engine. Previously, `sqlite:///./test.db` was passed verbatim to
# `create_async_engine`, which fails because the `pysqlite` driver is sync.
_settings = get_settings()
_normalized_url = _normalize_database_url(str(_settings.database_url))


_engine_kwargs: dict = {
    "echo": _settings.database_echo,
    "pool_pre_ping": True,
}
_connect_args = _build_connect_args(_normalized_url)
if _connect_args:
    _engine_kwargs["connect_args"] = _connect_args

# SQLite doesn't support pool sizing the same way as PG
if not _normalized_url.startswith("sqlite"):
    _engine_kwargs["pool_size"] = _settings.database_pool_size
    _engine_kwargs["max_overflow"] = _settings.database_max_overflow

engine = create_async_engine(_normalized_url, **_engine_kwargs)

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a transactional session."""
    async with SessionLocal() as session:
        yield session


def get_engine():
    """Return the global async engine (for tests / scripts)."""
    return engine


def reset_engine_for_tests() -> None:
    """Dispose the engine so a new one can be built after env change.

    Useful when tests flip DATABASE_URL between sqlite and a real DB.
    """
    import asyncio

    async def _dispose() -> None:
        await engine.dispose()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return
        loop.run_until_complete(_dispose())
    except RuntimeError:
        # No loop in this thread — best effort
        pass