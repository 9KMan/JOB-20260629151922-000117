"""Pipeline orchestrator — ties scraper + parser + db + outputs together.

A "run" does, for a single target:
  1. fetch raw HTML (via Playwright or httpx)
  2. parse records with selectolax CSS selectors
  3. validate with Pydantic
  4. upsert to PostgreSQL (idempotent)
  5. write CSV
  6. (optional) push to Google Sheets
  7. (optional) send Telegram summary
  8. record a Run row + DLQ rows on failure

The orchestrator exposes `run_target(target_name)` so it can be invoked
manually from a CLI or scheduled via APScheduler.
"""
from __future__ import annotations

import asyncio
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select

from bpa.config import get_settings
from bpa.db import SessionLocal
from bpa.logging_setup import get_logger
from bpa.pipeline.db.models import RunORM, ScraperTargetORM
from bpa.pipeline.db.upsert import bulk_upsert, finish_run, start_run
from bpa.pipeline.dlq import push_dead_letter
from bpa.pipeline.parsers.validate import NormalizedRecord
from bpa.pipeline.retry import retry_async
from bpa.pipeline.scrapers.base import (
    PermanentScraperError,
    Scraper,
    ScraperTarget,
    SelectorMap,
    TransientScraperError,
)
from bpa.pipeline.scrapers.http import HttpScraper, html_to_records

log = get_logger(__name__)


def target_from_orm(row: ScraperTargetORM) -> ScraperTarget:
    """Build a ScraperTarget dataclass from an ORM row."""
    selector_map_data = row.selector_map or {}
    row_sel = selector_map_data.get("row", ".row")
    fields = selector_map_data.get("fields", {})
    if not isinstance(fields, dict):
        fields = {}
    return ScraperTarget(
        id=row.id,
        name=row.name,
        url=row.url,
        mode=row.mode or "http",
        selector_map=SelectorMap(row=row_sel, fields=fields),
        schedule=row.schedule,
        enabled=row.enabled,
        extra={"orm": row},
    )


def target_from_dict(d: dict[str, Any]) -> ScraperTarget:
    """Build a ScraperTarget from a plain dict (e.g. parsed YAML)."""
    smap = d.get("selector_map") or {}
    return ScraperTarget(
        id=d.get("id"),
        name=d["name"],
        url=d["url"],
        mode=d.get("mode", "http"),
        selector_map=SelectorMap(
            row=smap.get("row", ".row"),
            fields=smap.get("fields", {}),
        ),
        schedule=d.get("schedule", "0 9 * * *"),
        enabled=d.get("enabled", True),
        extra=d.get("extra", {}),
    )


def make_scraper(mode: str) -> Scraper:
    """Factory: return the scraper instance for a given mode."""
    if mode == "playwright":
        from bpa.pipeline.scrapers.playwright import PlaywrightScraper

        return PlaywrightScraper()
    return HttpScraper()


@retry_async
async def _fetch_with_retry(scraper: Scraper, target: ScraperTarget) -> str:
    return await scraper.fetch(target)


def _parse_records(html: str, target: ScraperTarget) -> list[dict[str, Any]]:
    """Convert HTML to raw record dicts, then validate with Pydantic."""
    raw_records = html_to_records(html, target)
    validated: list[dict[str, Any]] = []
    for raw in raw_records:
        try:
            rec = NormalizedRecord.from_raw(raw)
            validated.append(rec.model_dump())
        except Exception as exc:  # noqa: BLE001 — skip bad rows, log warning
            log.warning(
                "parser.invalid_row",
                target=target.name,
                error=str(exc),
                raw=raw,
            )
    return validated


async def run_target(
    target: ScraperTarget,
    *,
    push_outputs: bool = True,
) -> dict[str, Any]:
    """Run a single scrape target end-to-end. Returns a run summary dict."""
    settings = get_settings()
    log.info(
        "pipeline.run.start",
        target=target.name,
        url=target.url,
        mode=target.mode,
    )
    scraper = make_scraper(target.mode)
    summary: dict[str, Any] = {
        "target": target.name,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "records_new": 0,
        "records_updated": 0,
        "errors": 0,
        "status": "running",
        "csv_path": None,
    }
    run_row: RunORM | None = None
    try:
        async with SessionLocal() as session:
            run_row = await start_run(session, target_id=target.id)
            await session.commit()
        try:
            html = await _fetch_with_retry(scraper, target)
        except (TransientScraperError, PermanentScraperError) as exc:
            summary["status"] = "failed"
            summary["error"] = str(exc)
            async with SessionLocal() as session:
                await push_dead_letter(
                    session,
                    target_id=target.id,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                    payload={"url": target.url, "mode": target.mode},
                )
                if run_row is not None:
                    await finish_run(
                        session,
                        run_row,
                        status="failed",
                        error_message=str(exc),
                    )
                await session.commit()
            summary["errors"] = 1
            log.error("pipeline.run.fetch_failed", target=target.name, error=str(exc))
            return summary

        records = _parse_records(html, target)
        async with SessionLocal() as session:
            new_count, updated_count = await bulk_upsert(
                session, target.id or 0, records, source_url=target.url
            )
            await session.commit()
        summary["records_new"] = new_count
        summary["records_updated"] = updated_count
        log.info(
            "pipeline.run.upserted",
            target=target.name,
            new=new_count,
            updated=updated_count,
        )

        # CSV export (mandatory)
        if records:
            from bpa.pipeline.outputs.csv_export import (
                default_csv_path,
                export_csv,
            )

            csv_path: Path = default_csv_path(target.name, base_dir=settings.csv_output_dir)
            enriched = [{**r, "target_id": target.id, "source_url": target.url} for r in records]
            written = export_csv(enriched, csv_path)
            summary["csv_path"] = str(written)
            log.info("pipeline.run.csv", target=target.name, path=str(written))

        # Optional outputs (only if explicitly enabled AND creds present)
        if push_outputs:
            try:
                from bpa.pipeline.outputs.sheets import push_to_sheet

                ok, msg = push_to_sheet(records, worksheet_name=target.name)
                summary["sheets"] = {"ok": ok, "message": msg}
            except Exception as exc:  # noqa: BLE001
                log.warning("pipeline.run.sheets_error", error=str(exc))
                summary["sheets"] = {"ok": False, "message": str(exc)}
            try:
                from bpa.pipeline.outputs.telegram import send_summary

                ok, msg = await send_summary(
                    target_name=target.name,
                    new_count=summary["records_new"],
                    updated_count=summary["records_updated"],
                )
                summary["telegram"] = {"ok": ok, "message": msg}
            except Exception as exc:  # noqa: BLE001
                log.warning("pipeline.run.telegram_error", error=str(exc))
                summary["telegram"] = {"ok": False, "message": str(exc)}

        summary["status"] = "success"
        async with SessionLocal() as session:
            if run_row is not None:
                await finish_run(
                    session,
                    run_row,
                    status="success",
                    records_new=summary["records_new"],
                    records_updated=summary["records_updated"],
                )
                await session.commit()
    except Exception as exc:  # noqa: BLE001
        summary["status"] = "failed"
        summary["error"] = str(exc)
        summary["trace"] = traceback.format_exc()
        async with SessionLocal() as session:
            try:
                await push_dead_letter(
                    session,
                    target_id=target.id,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                    payload={"trace": summary["trace"]},
                )
            except Exception:
                pass
            try:
                if run_row is not None:
                    await finish_run(
                        session,
                        run_row,
                        status="failed",
                        error_message=str(exc),
                    )
            except Exception:
                pass
            try:
                await session.commit()
            except Exception:
                pass
        log.error(
            "pipeline.run.exception",
            target=target.name,
            error=str(exc),
        )
    finally:
        try:
            await scraper.close()
        except Exception:
            pass
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        log.info(
            "pipeline.run.end",
            target=target.name,
            status=summary["status"],
            new=summary["records_new"],
            updated=summary["records_updated"],
        )
    return summary


async def run_target_by_name(name: str) -> dict[str, Any]:
    """Look up a target by name in the DB and run it."""
    async with SessionLocal() as session:
        stmt = select(ScraperTargetORM).where(ScraperTargetORM.name == name)
        row = (await session.execute(stmt)).scalar_one_or_none()
    if row is None:
        return {"status": "failed", "error": f"target {name!r} not found"}
    target = target_from_orm(row)
    return await run_target(target)


async def run_all_targets() -> list[dict[str, Any]]:
    """Run every enabled target sequentially."""
    async with SessionLocal() as session:
        stmt = select(ScraperTargetORM).where(ScraperTargetORM.enabled.is_(True))
        rows = (await session.execute(stmt)).scalars().all()
    results: list[dict[str, Any]] = []
    for row in rows:
        target = target_from_orm(row)
        results.append(await run_target(target))
    return results


def schedule_all_from_db() -> list[str]:
    """Read all enabled targets and register cron jobs for them."""
    from bpa.pipeline.schedulers.cron import add_cron_job, start_scheduler

    async def _collect() -> list[ScraperTargetORM]:
        async with SessionLocal() as session:
            stmt = select(ScraperTargetORM).where(ScraperTargetORM.enabled.is_(True))
            return list((await session.execute(stmt)).scalars().all())

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop is None:
        rows = asyncio.run(_collect())
    else:
        rows = loop.run_until_complete(_collect())
    job_ids: list[str] = []
    for row in rows:
        target = target_from_orm(row)
        job_id = add_cron_job(
            run_target_by_name,
            cron=target.schedule,
            job_id=f"scrape:{target.name}",
            kwargs={"name": target.name},
        )
        job_ids.append(job_id)
    start_scheduler()
    return job_ids


__all__ = [
    "make_scraper",
    "run_all_targets",
    "run_target",
    "run_target_by_name",
    "schedule_all_from_db",
    "target_from_dict",
    "target_from_orm",
]