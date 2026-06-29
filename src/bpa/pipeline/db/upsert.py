"""Idempotent upserts and run-tracking helpers.

These are written as plain SQL (with SQLAlchemy Core) instead of ORM
`merge()` so we can lean on the database's `ON CONFLICT` semantics and get
atomic, race-free dedup behaviour.

The upsert returns `(new_count, updated_count)` so the orchestrator can
update the Run row accurately.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from bpa.pipeline.db.models import DeadLetterORM, RecordORM, RunORM


def _is_sqlite(session: AsyncSession) -> bool:
    return session.bind is not None and session.bind.dialect.name == "sqlite"


async def upsert_record(
    session: AsyncSession,
    *,
    target_id: int,
    external_id: str,
    payload: dict[str, Any],
    source_url: str | None,
) -> tuple[bool, bool]:
    """Upsert a single record, returning (was_inserted, was_updated).

    Uses ON CONFLICT DO UPDATE on PostgreSQL and the equivalent SQLite
    `ON CONFLICT(target_id, external_id) DO UPDATE` so the same code runs
    against either database.
    """
    values = {
        "target_id": target_id,
        "external_id": external_id,
        "payload": payload,
        "source_url": source_url,
        "scraped_at": datetime.now(timezone.utc),
    }
    if _is_sqlite(session):
        stmt = sqlite_insert(RecordORM).values(**values)
        # SQLite syntax is identical to PG for ON CONFLICT DO UPDATE
        stmt = stmt.on_conflict_do_update(
            index_elements=["target_id", "external_id"],
            set_={
                "payload": stmt.excluded.payload,
                "source_url": stmt.excluded.source_url,
                "scraped_at": stmt.excluded.scraped_at,
            },
        )
    else:
        stmt = pg_insert(RecordORM).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["target_id", "external_id"],
            set_={
                "payload": stmt.excluded.payload,
                "source_url": stmt.excluded.source_url,
                "scraped_at": stmt.excluded.scraped_at,
            },
        )

    result = await session.execute(stmt)
    # result.rowcount on upsert: 1 if insert, 2 if update (SQLAlchemy
    # convention). We map that to (inserted, updated) booleans.
    inserted = result.rowcount == 1
    updated = result.rowcount == 2
    return inserted, updated


async def bulk_upsert(
    session: AsyncSession,
    target_id: int,
    records: list[dict[str, Any]],
    source_url: str | None = None,
) -> tuple[int, int]:
    """Upsert many records sequentially.

    Returns (new_count, updated_count).
    """
    new = 0
    updated = 0
    for rec in records:
        ext = rec.get("external_id") or rec.get("id") or rec.get("name")
        if not ext:
            # No dedup key — skip to avoid an unkeyed row
            continue
        inserted, was_updated = await upsert_record(
            session,
            target_id=target_id,
            external_id=str(ext),
            payload=rec,
            source_url=source_url or rec.get("source_url") or rec.get("url"),
        )
        if inserted:
            new += 1
        elif was_updated:
            updated += 1
    return new, updated


async def start_run(
    session: AsyncSession, *, target_id: int | None, status: str = "running"
) -> RunORM:
    """Insert a new run row and return it (not yet flushed)."""
    run = RunORM(target_id=target_id, status=status)
    session.add(run)
    await session.flush()
    return run


async def finish_run(
    session: AsyncSession,
    run: RunORM,
    *,
    status: str,
    records_new: int = 0,
    records_updated: int = 0,
    error_message: str | None = None,
) -> None:
    """Mark a run complete with final counts / error."""
    run.status = status
    run.records_new = records_new
    run.records_updated = records_updated
    run.error_message = error_message
    run.finished_at = datetime.now(timezone.utc)
    await session.flush()


async def record_dead_letter(
    session: AsyncSession,
    *,
    target_id: int | None,
    external_id: str | None,
    error_type: str,
    error_message: str,
    payload: dict[str, Any] | None = None,
    attempt_count: int = 1,
) -> DeadLetterORM:
    """Persist a permanent failure to the dead_letter table."""
    dlq = DeadLetterORM(
        target_id=target_id,
        external_id=external_id,
        error_type=error_type,
        error_message=error_message,
        payload=payload or {},
        attempt_count=attempt_count,
    )
    session.add(dlq)
    await session.flush()
    return dlq


__all__ = [
    "bulk_upsert",
    "finish_run",
    "record_dead_letter",
    "start_run",
    "upsert_record",
]