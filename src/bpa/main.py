"""FastAPI application entry point."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from sqlalchemy import select

from bpa.config import get_settings
from bpa.db import SessionLocal
from bpa.logging_setup import configure_logging, get_logger
from bpa.pipeline.db.models import RunORM, init_models


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log = get_logger(__name__)
    settings = get_settings()
    log.info("app.starting", env=settings.environment, name=settings.app_name)
    try:
        await init_models()
    except Exception as exc:  # noqa: BLE001
        log.warning("app.init_models_failed", error=str(exc))
    yield
    log.info("app.stopped")


app = FastAPI(
    title="BPA Pipeline",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe — returns ok plus the most recent run timestamp."""
    settings = get_settings()
    payload: dict[str, str] = {"status": "ok", "environment": settings.environment}
    try:
        async with SessionLocal() as session:
            stmt = select(RunORM).order_by(RunORM.id.desc()).limit(1)
            row = (await session.execute(stmt)).scalar_one_or_none()
            if row is not None:
                ts = row.started_at
                payload["last_run"] = (
                    ts.isoformat() if isinstance(ts, datetime) else str(ts)
                )
                payload["last_status"] = row.status
            else:
                payload["last_run"] = "never"
                payload["last_status"] = "n/a"
    except Exception:  # noqa: BLE001
        # Health probe must never raise
        payload["db"] = "unreachable"
    payload["server_time"] = datetime.now(timezone.utc).isoformat()
    return payload


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "BPA Pipeline", "version": "0.1.0"}