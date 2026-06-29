"""Dead-letter queue helpers — wraps the dead_letter table with conveniences."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bpa.pipeline.db.models import DeadLetterORM


async def push_dead_letter(
    session: AsyncSession,
    *,
    target_id: int | None,
    error_type: str,
    error_message: str,
    external_id: str | None = None,
    payload: dict[str, Any] | None = None,
    attempt_count: int = 1,
) -> DeadLetterORM:
    """Persist a permanent failure and return the new row."""
    from bpa.pipeline.db.upsert import record_dead_letter

    return await record_dead_letter(
        session,
        target_id=target_id,
        external_id=external_id,
        error_type=error_type,
        error_message=error_message,
        payload=payload or {},
        attempt_count=attempt_count,
    )


async def list_dead_letters(
    session: AsyncSession, *, limit: int = 100
) -> list[DeadLetterORM]:
    """Return the most recent DLQ rows."""
    stmt = (
        select(DeadLetterORM)
        .order_by(DeadLetterORM.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def count_dead_letters(
    session: AsyncSession, *, target_id: int | None = None
) -> int:
    """Count dead-letter rows, optionally filtered by target."""
    stmt = select(DeadLetterORM)
    if target_id is not None:
        stmt = stmt.where(DeadLetterORM.target_id == target_id)
    result = await session.execute(stmt)
    return len(list(result.scalars().all()))


def alert_message(errors: list[DeadLetterORM]) -> str:
    """Build a short human-readable alert message from DLQ rows."""
    if not errors:
        return ""
    lines = ["Dead-letter alert:"]
    for e in errors[:10]:
        lines.append(
            f"- target={e.target_id} ext={e.external_id} type={e.error_type}: {e.error_message}"
        )
    if len(errors) > 10:
        lines.append(f"...and {len(errors) - 10} more")
    return "\n".join(lines)


__all__ = ["alert_message", "count_dead_letters", "list_dead_letters", "push_dead_letter"]