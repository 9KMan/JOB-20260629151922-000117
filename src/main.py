"""Alembic environment - uses async SQLAlchemy engine from bpa.db."""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import the application settings
from bpa.config import get_settings

# NOTE: when models are added in later phases, import them here so their
# tables register on Base.metadata and `target_metadata = Base.metadata`
# picks them up. Example:
#     from bpa.models import Base
#     target_metadata = Base.metadata
target_metadata = None  # will be replaced once models exist


config = context.config

# Override sqlalchemy.url from application settings (env var wins)
settings = get_settings()
config.set_main_option("sqlalchemy.url", str(settings.database_url))


def _configure_logging() -> None:
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    _configure_logging()
    run_migrations_online()
