"""Alembic environment - uses async SQLAlchemy engine from bpa.config.

We use synchronous-mode Alembic with an async-aware engine by running
the migration in a synchronous context through the URL swap. The actual
async URL is read from bpa.config and converted to a sync URL (psycopg2
driver) so Alembic can run migrations without an async event loop.
"""
from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from bpa.config import get_settings


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()

# Convert async URL (asyncpg) to sync URL (psycopg2) for Alembic runtime.
# We keep the sync DSN in alembic.ini-less mode by passing it through here.
_sync_url = str(settings.database_url).replace(
    "postgresql+asyncpg://", "postgresql+psycopg2://"
)
config.set_main_option("sqlalchemy.url", _sync_url)

target_metadata = None  # Models will be wired in a later phase.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
