"""Alembic environment - uses async SQLAlchemy engine.

Reads the database URL from ``bpa.config.Settings`` so there is a single
source of truth for connection settings (env vars + .env file).
"""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import settings so we can pull the DSN at migration time.
from bpa.config import get_settings

# This is the Alembic Config object, which provides access to the values
# within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata is wired up in a later phase when SQLAlchemy models land.
# For Phase 1 we keep autogenerate disabled (target_metadata = None).
target_metadata = None


def get_database_url() -> str:
    """Return the async DSN from application settings."""
    return str(get_settings().database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emits SQL without a DB connection)."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations against an established sync connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
