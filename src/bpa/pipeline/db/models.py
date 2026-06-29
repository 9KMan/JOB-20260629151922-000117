"""SQLAlchemy ORM models for the BPA pipeline.

We use the SQLAlchemy 2.0 declarative API with `Mapped[]` annotations. JSONB
columns (PostgreSQL-only) degrade to plain JSON on SQLite so the test suite
can run without a Postgres server.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative base for all models."""

    pass


class ScraperTargetORM(Base):
    """Configuration row describing a single website to scrape."""

    __tablename__ = "scraper_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    selector_map: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    schedule: Mapped[str] = mapped_column(String(64), default="0 9 * * *", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    mode: Mapped[str] = mapped_column(String(32), default="http", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    records: Mapped[list["RecordORM"]] = relationship(back_populates="target")
    runs: Mapped[list["RunORM"]] = relationship(back_populates="target")


class RecordORM(Base):
    """A normalized scraped record.

    Idempotency: UNIQUE(target_id, external_id) so the orchestrator can use
    `ON CONFLICT DO UPDATE` to upsert without producing duplicates.
    """

    __tablename__ = "records"
    __table_args__ = (UniqueConstraint("target_id", "external_id", name="uq_records_target_ext"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_id: Mapped[int] = mapped_column(
        ForeignKey("scraper_targets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    target: Mapped[ScraperTargetORM] = relationship(back_populates="records")


class RunORM(Base):
    """Execution history row — one per orchestrator pass."""

    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_id: Mapped[int | None] = mapped_column(
        ForeignKey("scraper_targets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)
    records_new: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    target: Mapped[ScraperTargetORM | None] = relationship(back_populates="runs")


class DeadLetterORM(Base):
    """Persistence for permanent failures.

    Unlike an in-memory DLQ, these rows survive process restarts and give
    operators a queryable history of what went wrong.
    """

    __tablename__ = "dead_letter"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target_id: Mapped[int | None] = mapped_column(
        ForeignKey("scraper_targets.id", ondelete="SET NULL"), nullable=True
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_type: Mapped[str] = mapped_column(String(64), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )


async def init_models() -> None:
    """Create all tables in the configured database (idempotent)."""
    from bpa.db import engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)