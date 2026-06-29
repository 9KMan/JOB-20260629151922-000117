## Phase Goal
Define the PostgreSQL data model for the ETL pipeline: entities, fields, relationships, indexes, and storage approach using SQLAlchemy 2.0 async ORM with Alembic migrations.

## Files to Create

```file:src/models/__init__.py
"""SQLAlchemy ORM models for the scraping pipeline."""
from src.models.base import Base
from src.models.source import Source
from src.models.scraped_record import ScrapedRecord
from src.models.scrape_run import ScrapeRun
from src.models.dead_letter import DeadLetter

__all__ = [
    "Base",
    "Source",
    "ScrapeRun",
    "ScrapedRecord",
    "DeadLetter",
]
```

```file:src/models/base.py
"""Declarative base and shared mixins."""
from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Centralized naming convention keeps Alembic autogen diffs deterministic.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
```

```file:src/models/source.py
"""A target website/endpoint the pipeline scrapes."""
from __future__ import annotations

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.models.base import Base, TimestampMixin


class ScrapeStrategy(str, enum.Enum):
    PLAYWRIGHT = "playwright"
    HTTPX = "httpx"


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    base_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    strategy: Mapped[ScrapeStrategy] = mapped_column(
        SAEnum(ScrapeStrategy, name="scrape_strategy"),
        nullable=False,
        default=ScrapeStrategy.PLAYWRIGHT,
    )
    schedule_cron: Mapped[str] = mapped_column(String(64), nullable=False, default="0 * * * *")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    runs: Mapped[List["ScrapeRun"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
        order_by="desc(ScrapeRun.started_at)",
    )
    records: Mapped[List["ScrapedRecord"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )
```

```file:src/models/scrape_run.py
"""One execution attempt of a Source scrape."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.models.base import Base, TimestampMixin


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class ScrapeRun(Base, TimestampMixin):
    __tablename__ = "scrape_runs"
    __table_args__ = (
        Index("ix_scrape_runs_source_started", "source_id", "started_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[RunStatus] = mapped_column(
        SAEnum(RunStatus, name="run_status"),
        nullable=False,
        default=RunStatus.PENDING,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    items_fetched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_written: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    source: Mapped["Source"] = relationship(back_populates="runs")  # noqa: F821
    records: Mapped[List["ScrapedRecord"]] = relationship(  # noqa: F821
        back_populates="run",
        cascade="all, delete-orphan",
    )
```

```file:src/models/scraped_record.py
"""A single cleaned business record produced by a scrape."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Any
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class ScrapedRecord(Base, TimestampMixin):
    """
    Normalized row + raw payload. The external_id + source_id pair is the
    natural idempotency key — re-scraping the same item upserts instead of
    duplicating.
    """

    __tablename__ = "scraped_records"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_records_source_external"),
        Index("ix_records_source_created", "source_id", "created_at"),
        Index("ix_records_payload_gin", "payload", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    run_id: Mapped[int] = mapped_column(
        ForeignKey("scrape_runs.id", ondelete="SET NULL"), nullable=True
    )
    external_id: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    source: Mapped["Source"] = relationship(back_populates="records")  # noqa: F821
    run: Mapped[Optional["ScrapeRun"]] = relationship(back_populates="records")  # noqa: F821
```

```file:src/models/dead_letter.py
"""Dead-letter queue entries for runs that exhausted retries."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Any
from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin


class DeadLetter(Base, TimestampMixin):
    __tablename__ = "dead_letters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    run_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("scrape_runs.id", ondelete="SET NULL"), nullable=True
    )
    error_type: Mapped[str] = mapped_column(String(120), nullable=False)
    error_message: Mapped[str] = mapped_column(String(4000), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
    )
    failed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

```file:src/schemas/__init__.py
"""Pydantic v2 domain models used at the application boundary."""
from src.schemas.source import SourceCreate, SourceRead, SourceUpdate
from src.schemas.record import ScrapedRecordCreate, ScrapedRecordRead
from src.schemas.run import ScrapeRunRead, RunStatus

__all__ = [
    "SourceCreate",
    "SourceRead",
    "SourceUpdate",
    "ScrapedRecordCreate",
    "ScrapedRecordRead",
    "ScrapeRunRead",
    "RunStatus",
]
```

```file:src/schemas/source.py
"""Pydantic schemas for the Source entity."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from src.models.source import ScrapeStrategy


class SourceBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    base_url: HttpUrl
    strategy: ScrapeStrategy = ScrapeStrategy.PLAYWRIGHT
    schedule_cron: str = Field(default="0 * * * *", max_length=64)
    is_active: bool = True
    rate_limit_per_minute: int = Field(default=30, ge=1, le=600)


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    base_url: HttpUrl | None = None
    strategy: ScrapeStrategy | None = None
    schedule_cron: str | None = Field(default=None, max_length=64)
    is_active: bool | None = None
    rate_limit_per_minute: int | None = Field(default=None, ge=1, le=600)


class SourceRead(SourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_scraped_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

```file:src/schemas/record.py
"""Pydantic schemas for ScrapedRecord."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ScrapedRecordCreate(BaseModel):
    external_id: str = Field(min_length=1, max_length=512)
    title: str | None = Field(default=None, max_length=1024)
    url: HttpUrl | None = None
    content_hash: str = Field(min_length=8, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)
    scraped_at: datetime


class ScrapedRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    run_id: int | None
    external_id: str
    title: str | None
    url: str | None
    content_hash: str
    payload: dict[str, Any]
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime
```

```file:src/schemas/run.py
"""Pydantic schemas for ScrapeRun."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.models.scrape_run import RunStatus


class ScrapeRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    status: RunStatus
    started_at: datetime
    finished_at: datetime | None
    items_fetched: int
    items_written: int
    error_message: str | None
    attempt_number: int
    created_at: datetime
    updated_at: datetime
```

```file:alembic.ini
# Minimal Alembic config — full path configured via env.py
[alembic]
script_location = migrations
prepend_sys_path = .
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

```file:migrations/env.py
"""Alembic environment using async SQLAlchemy + asyncpg."""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.core.config import settings
from src.models import Base  # noqa: F401  registers all tables

config = context.config
config.set_main_option("sqlalchemy.url", settings.async_database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


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


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
```

```file:migrations/script.py.mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

```file:migrations/versions/0001_initial.py
"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-29 15:19:22
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    scrape_strategy = postgresql.ENUM(
        "playwright", "httpx", name="scrape_strategy", create_type=False
    )
    run_status = postgresql.ENUM(
        "pending", "running", "success", "partial", "failed",
        name="run_status", create_type=False,
    )
    scrape_strategy.create(op.get_bind(), checkfirst=True)
    run_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "sources",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("base_url", sa.String(2048), nullable=False),
        sa.Column("strategy", scrape_strategy, nullable=False, server_default="playwright"),
        sa.Column("schedule_cron", sa.String(64), nullable=False, server_default="0 * * * *"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("rate_limit_per_minute", sa.Integer, nullable=False, server_default="30"),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sources_name", "sources", ["name"], unique=True)

    op.create_table(
        "scrape_runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", run_status, nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("items_fetched", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_written", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.String(2000), nullable=True),
        sa.Column("attempt_number", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_scrape_runs_source_started", "scrape_runs", ["source_id", "started_at"])

    op.create_table(
        "scraped_records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_id", sa.Integer, sa.ForeignKey("scrape_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("external_id", sa.String(512), nullable=False),
        sa.Column("title", sa.String(1024), nullable=True),
        sa.Column("url", sa.String(2048), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source_id", "external_id", name="uq_records_source_external"),
    )
    op.create_index("ix_records_source_created", "scraped_records", ["source_id", "created_at"])
    op.create_index("ix_records_payload_gin", "scraped_records", ["payload"], postgresql_using="gin")

    op.create_table(
        "dead_letters",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_id", sa.Integer, sa.ForeignKey("scrape_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("error_type", sa.String(120), nullable=False),
        sa.Column("error_message", sa.String(4000), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("dead_letters")
    op.drop_index("ix_records_payload_gin", table_name="scraped_records")
    op.drop_index("ix_records_source_created", table_name="scraped_records")
    op.drop_table("scraped_records")
    op.drop_index("ix_scrape_runs_source_started", table_name="scrape_runs")
    op.drop_table("scrape_runs")
    op.drop_index("ix_sources_name", table_name="sources")
    op.drop_table("sources")
    op.execute("DROP TYPE IF EXISTS run_status")
    op.execute("DROP TYPE IF EXISTS scrape_strategy")
```

```file:src/core/config.py
"""Settings singleton — referenced by Alembic env.py."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):