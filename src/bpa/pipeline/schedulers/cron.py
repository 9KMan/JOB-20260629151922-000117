"""APScheduler configuration and job registration helpers.

We use BackgroundScheduler (in-process) since the SPEC calls for a single-
host MVP. Switch to AsyncIOScheduler if you embed the scheduler inside an
already-running event loop.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from bpa.config import get_settings

# APScheduler logs are very chatty — silence them
logging.getLogger("apscheduler").setLevel(logging.WARNING)


_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    """Return the singleton BackgroundScheduler."""
    global _scheduler
    if _scheduler is None:
        settings = get_settings()
        _scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
    return _scheduler


def add_cron_job(
    func: Callable[..., Any],
    *,
    cron: str = "0 9 * * *",
    job_id: str | None = None,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
) -> str:
    """Register a cron job on the singleton scheduler.

    Returns the job_id.
    """
    scheduler = get_scheduler()
    trigger = CronTrigger.from_crontab(cron)
    job = scheduler.add_job(
        func,
        trigger=trigger,
        args=args,
        kwargs=kwargs or {},
        id=job_id,
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    return job.id


def start_scheduler() -> None:
    """Start the scheduler (idempotent)."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()


def shutdown_scheduler() -> None:
    """Shutdown the scheduler if it's running."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None


__all__ = [
    "add_cron_job",
    "get_scheduler",
    "shutdown_scheduler",
    "start_scheduler",
]