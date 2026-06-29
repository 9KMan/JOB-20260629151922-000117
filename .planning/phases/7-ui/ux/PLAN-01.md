# PLAN-01.md — Phase 7: UI/UX

## Phase Goal
Define the user interface approach, layout patterns, and UX flows for a minimal operator-facing control panel (FastAPI-served HTML/HTMX + Telegram bot) that exposes scraping job status, manual triggers, and CSV exports.

## Files to Create

```file:app/ui/__init__.py
"""UI package: server-side rendered HTML pages, HTMX partials, and Telegram bot handlers."""
from app.ui.routes import router
from app.ui.telegram import TelegramBotService

__all__ = ["router", "TelegramBotService"]
```

```file:app/ui/templates/base.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Scraper Console{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <h1>📊 Scraper Console</h1>
            <span class="subtitle">Job JOB-20260629151922-000117</span>
        </div>
        <ul class="nav-links">
            <li><a href="/" class="{% if active=='dashboard' %}active{% endif %}">Dashboard</a></li>
            <li><a href="/jobs" class="{% if active=='jobs' %}active{% endif %}">Jobs</a></li>
            <li><a href="/runs" class="{% if active=='runs' %}active{% endif %}">Runs</a></li>
            <li><a href="/exports" class="{% if active=='exports' %}active{% endif %}">Exports</a></li>
        </ul>
    </nav>

    <main class="container">
        {% if flash %}
        <div class="flash flash-{{ flash.type }}">{{ flash.message }}</div>
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    <footer class="footer">
        <span>Last refresh: <span id="last-refresh">{{ now }}</span></span>
        <span>Pipeline status: <span hx-get="/health/light" hx-trigger="load, every 30s" hx-swap="innerHTML">checking...</span></span>
    </footer>
</body>
</html>
```

```file:app/ui/templates/dashboard.html
{% extends "base.html" %}
{% block title %}Dashboard — Scraper Console{% endblock %}
{% block content %}
<section class="kpi-grid">
    <div class="kpi-card" id="kpi-jobs">
        <div class="kpi-label">Active Jobs</div>
        <div class="kpi-value" hx-get="/api/kpi/active-jobs" hx-trigger="load, every 15s" hx-swap="innerHTML">—</div>
    </div>
    <div class="kpi-card" id="kpi-runs">
        <div class="kpi-label">Runs (24h)</div>
        <div class="kpi-value" hx-get="/api/kpi/runs-24h" hx-trigger="load, every 15s" hx-swap="innerHTML">—</div>
    </div>
    <div class="kpi-card" id="kpi-records">
        <div class="kpi-label">Records Stored</div>
        <div class="kpi-value" hx-get="/api/kpi/records-total" hx-trigger="load, every 30s" hx-swap="innerHTML">—</div>
    </div>
    <div class="kpi-card" id="kpi-failures">
        <div class="kpi-label">Failures (24h)</div>
        <div class="kpi-value" hx-get="/api/kpi/failures-24h" hx-trigger="load, every 15s" hx-swap="innerHTML">—</div>
    </div>
</section>

<section class="recent-runs">
    <h2>Recent Runs</h2>
    <div hx-get="/runs/recent-partial" hx-trigger="load, every 10s" hx-swap="innerHTML">
        Loading recent runs...
    </div>
</section>
{% endblock %}
```

```file:app/ui/templates/jobs.html
{% extends "base.html" %}
{% block title %}Jobs — Scraper Console{% endblock %}
{% block content %}
<div class="page-header">
    <h2>Scraping Jobs</h2>
    <a href="/jobs/new" class="btn btn-primary">+ New Job</a>
</div>

<div class="filter-bar">
    <input type="search" name="q" placeholder="Search jobs..." hx-get="/jobs/list-partial" hx-trigger="input changed delay:300ms" hx-target="#jobs-table" hx-include="this">
    <select name="status" hx-get="/jobs/list-partial" hx-trigger="change" hx-target="#jobs-table" hx-include="[name='q']">
        <option value="">All</option>
        <option value="active">Active</option>
        <option value="paused">Paused</option>
        <option value="failed">Failed</option>
    </select>
</div>

<div id="jobs-table" hx-get="/jobs/list-partial" hx-trigger="load" hx-swap="innerHTML">
    Loading jobs...
</div>
{% endblock %}
```

```file:app/ui/templates/jobs_list_partial.html
<table class="data-table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Source URL</th>
            <th>Schedule</th>
            <th>Status</th>
            <th>Last Run</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for job in jobs %}
        <tr>
            <td><a href="/jobs/{{ job.id }}">{{ job.name }}</a></td>
            <td class="truncate">{{ job.source_url }}</td>
            <td><code>{{ job.cron_expression }}</code></td>
            <td><span class="badge badge-{{ job.status }}">{{ job.status }}</span></td>
            <td>{{ job.last_run_at or 'never' }}</td>
            <td class="actions">
                <button hx-post="/jobs/{{ job.id }}/trigger" hx-swap="none" class="btn btn-sm">▶ Run</button>
                <button hx-post="/jobs/{{ job.id }}/pause" hx-swap="none" class="btn btn-sm">⏸ Pause</button>
            </td>
        </tr>
        {% else %}
        <tr><td colspan="6" class="empty">No jobs configured. <a href="/jobs/new">Create one</a>.</td></tr>
        {% endfor %}
    </tbody>
</table>
```

```file:app/ui/templates/runs.html
{% extends "base.html" %}
{% block title %}Runs — Scraper Console{% endblock %}
{% block content %}
<h2>Pipeline Runs</h2>
<div class="filter-bar">
    <select name="status" hx-get="/runs/list-partial" hx-trigger="change" hx-target="#runs-table">
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="running">Running</option>
        <option value="success">Success</option>
        <option value="failed">Failed</option>
        <option value="dlq">Dead-lettered</option>
    </select>
</div>

<div id="runs-table" hx-get="/runs/list-partial" hx-trigger="load, every 10s" hx-swap="innerHTML">
    Loading runs...
</div>
{% endblock %}
```

```file:app/ui/templates/runs_recent_partial.html
<table class="data-table compact">
    <thead>
        <tr><th>Job</th><th>Status</th><th>Records</th><th>Duration</th><th>Started</th></tr>
    </thead>
    <tbody>
        {% for run in runs %}
        <tr>
            <td>{{ run.job_name }}</td>
            <td><span class="badge badge-{{ run.status }}">{{ run.status }}</span></td>
            <td>{{ run.records_count }}</td>
            <td>{{ run.duration_ms }}ms</td>
            <td>{{ run.started_at }}</td>
        </tr>
        {% else %}
        <tr><td colspan="5" class="empty">No runs yet.</td></tr>
        {% endfor %}
    </tbody>
</table>
```

```file:app/ui/routes.py
"""HTTP routes for the operator UI: pages + HTMX partials + JSON KPI endpoints."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Job, Run, Record, Export
from app.db.session import get_session
from app.schemas.jobs import JobCreate, JobOut
from app.services.scheduler import trigger_job_now
from app.services.export import generate_csv

router = APIRouter()
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: AsyncSession = Depends(get_session)) -> HTMLResponse:
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "active": "dashboard", "now": datetime.utcnow().isoformat(timespec="seconds")},
    )


@router.get("/jobs", response_class=HTMLResponse)
async def jobs_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("jobs.html", {"request": request, "active": "jobs"})


@router.get("/jobs/list-partial", response_class=HTMLResponse)
async def jobs_list_partial(
    request: Request,
    q: str = "",
    status: str = "",
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    stmt = select(Job)
    if q:
        stmt = stmt.where(Job.name.ilike(f"%{q}%"))
    if status:
        stmt = stmt.where(Job.status == status)
    stmt = stmt.order_by(Job.created_at.desc()).limit(50)
    result = await session.execute(stmt)
    jobs = result.scalars().all()
    return templates.TemplateResponse("jobs_list_partial.html", {"request": request, "jobs": jobs})


@router.post("/jobs/{job_id}/trigger")
async def trigger_job(job_id: int) -> JSONResponse:
    await trigger_job_now(job_id)
    return JSONResponse({"ok": True, "job_id": job_id})


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: int, session: AsyncSession = Depends(get_session)) -> JSONResponse:
    job = await session.get(Job, job_id)
    if job:
        job.status = "paused"
        await session.commit()
    return JSONResponse({"ok": True, "job_id": job_id, "status": "paused"})


@router.get("/runs", response_class=HTMLResponse)
async def runs_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("runs.html", {"request": request, "active": "runs"})


@router.get("/runs/list-partial", response_class=HTMLResponse)
async def runs_list_partial(
    request: Request,
    status: str = "",
    session: AsyncSession = Depends(get_session),
) -> HTMLResponse:
    stmt = select(Run).order_by(Run.started_at.desc()).limit(100)
    if status:
        stmt = stmt.where(Run.status == status)
    result = await session.execute(stmt)
    runs = result.scalars().all()
    return templates.TemplateResponse("runs_list_partial.html", {"request": request, "runs": runs})


@router.get("/runs/recent-partial", response_class=HTMLResponse)
async def runs_recent_partial(request: Request, session: AsyncSession = Depends(get_session)) -> HTMLResponse:
    stmt = select(Run).order_by(Run.started_at.desc()).limit(5)
    result = await session.execute(stmt)
    runs = result.scalars().all()
    return templates.TemplateResponse("runs_recent_partial.html", {"request": request, "runs": runs})


@router.get("/exports", response_class=HTMLResponse)
async def exports_page(request: Request, session: AsyncSession = Depends(get_session)) -> HTMLResponse:
    stmt = select(Export).order_by(Export.created_at.desc()).limit(50)
    result = await session.execute(stmt)
    exports = result.scalars().all()
    return templates.TemplateResponse("exports.html", {"request": request, "exports": exports, "active": "exports"})


@router.get("/api/kpi/active-jobs")
async def kpi_active_jobs(session: AsyncSession = Depends(get_session)) -> JSONResponse:
    count = await session.scalar(select(func.count(Job.id)).where(Job.status == "active"))
    return JSONResponse({"value": count or 0})


@router.get("/api/kpi/runs-24h")
async def kpi_runs_24h(session: AsyncSession = Depends(get_session)) -> JSONResponse:
    since = datetime.utcnow() - timedelta(hours=24)
    count = await session.scalar(select(func.count(Run.id)).where(Run.started_at >= since))
    return JSONResponse({"value": count or 0})


@router.get("/api/kpi/records-total")
async def kpi_records_total(session: AsyncSession = Depends(get_session)) -> JSONResponse:
    count = await session.scalar(select(func.count(Record.id)))
    return JSONResponse({"value": count or 0})


@router.get("/api/kpi/failures-24h")
async def kpi_failures_24h(session: AsyncSession = Depends(get_session)) -> JSONResponse:
    since = datetime.utcnow() - timedelta(hours=24)
    count = await session.scalar(
        select(func.count(Run.id)).where(Run.started_at >= since, Run.status == "failed")
    )
    return JSONResponse({"value": count or 0})


@router.get("/health/light")
async def health_light(session: AsyncSession = Depends(get_session)) -> HTMLResponse:
    try:
        await session.execute(select(1))
        return HTMLResponse("<span class='status-ok'>● healthy</span>")
    except Exception:
        return HTMLResponse("<span class='status-fail'>● unreachable</span>")
```

```file:app/ui/telegram.py
"""Telegram bot handler: command parsing, summary delivery, alerts."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Job, Run, Record
from app.services.export import generate_csv
from app.services.scheduler import trigger_job_now

logger = logging.getLogger(__name__)
router = Router()


class TelegramBotService:
    """Wraps aiogram lifecycle; mounted on FastAPI startup/shutdown events."""

    def __init__(self, token: str) -> None:
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.dp.include_router(router)

    async def start(self) -> None:
        logger.info("Telegram bot polling started")
        await self.dp.start_polling(self.bot)

    async def stop(self) -> None:
        await self.bot.session.close()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Scraper Console Bot\n\n"
        "Commands:\n"
        "/status — pipeline summary\n"
        "/jobs — list active jobs\n"
        "/run <job_id> — trigger a job now\n"
        "/export <job_id> — request CSV export"
    )


@router.message(Command("status"))
async def cmd_status(message: Message, session: AsyncSession) -> None:
    since = datetime.utcnow() - timedelta(hours=24)
    runs_24h = await session.scalar(select(func.count(Run.id)).where(Run.started_at >= since))
    failures_24h = await session.scalar(
        select(func.count(Run.id)).where(Run.started_at >= since, Run.status == "failed")
    )
    records_total = await session.scalar(select(func.count(Record.id)))
    active_jobs = await session.scalar(select(func.count(Job.id)).where(Job.status == "active"))

    text = (
        "📊 *Pipeline Status*\n\n"
        f"Active jobs: *{active_jobs or 0}*\n"
        f"Runs (24h): *{runs_24h or 0}*\n"
        f"Failures (24h): *{failures_24h or 0}*\n"
        f"Records stored: *{records_total or 0}*\n"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("jobs"))
async def cmd_jobs(message: Message, session: AsyncSession) -> None:
    result = await session.execute(select(Job).where(Job.status == "active").limit(20))
    jobs = result.scalars().all()
    if not jobs:
        await message.answer("No active jobs.")
        return
    lines = ["🗂 *Active Jobs*\n"]
    for j in jobs:
        lines.append(f"• #{j.id} {j.name} — `{j.cron_expression}`")
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(Command("run"))
async def cmd_run(message: Message) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Usage: /run <job_id>")
        return
    job_id = int(parts[1])
    await trigger_job_now(job_id)
    await message.answer(f"✅ Triggered job #{job_id}")


@router.message(Command("export"))
async def cmd_export(message: Message, session: AsyncSession) -> None:
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Usage: /export <job_id>")
        return
    job_id = int(parts[1])
    path = await generate_csv(session, job_id)
    await message.answer_document(document=path, caption=f"Export for job #{job_id}")
```

```file:app/ui/static/css/style.css
:root {
    --bg: #0f172a;
    --surface: #1e293b;
    --surface-2: #334155;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --success: #22c55e;
    --warn: #f59e0b;
    --danger: #ef4444;
    --radius: 8px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
    min-height: 100vh;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: var(--surface);
    border-bottom: 1px solid var(--surface-2);
}

.nav-brand h1 { font-size: 1.25rem; }
.subtitle { color: var(--muted); font-size: 0.85rem; }

.nav-links { display: flex; list-style: none; gap: 1.5rem; }
.nav-links a { color: var(--muted); text-decoration: none; padding: 0.5rem 0.75rem; border-radius: var(--radius); }
.nav-links a.active, .nav-links a:hover { color: var(--text); background: var(--surface-2); }

.container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.kpi-card {
    background: var(--surface);
    padding: 1.25rem;
    border-radius: var(--radius);
    border: 1px solid var(--surface-2);
}
.kpi-label { color: var(--muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-value { font-size: 2rem; font-weight: 600; margin-top: 0.5rem; color: var(--accent); }

.data-table { width: 100%; border-collapse: collapse; background: var(--surface); border-radius: var(--radius); overflow: hidden; }
.data-table th, .data-table td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--surface-2); }
.data-table th { background: var(--surface-2); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }
.data-table tr:hover { background: var(--surface-2); }
.data-table .truncate { max-width: 240px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.data-table .empty { text-align: center; color: var(--muted); padding: 2rem; }
.data-table.compact th, .data-table.compact td { padding: 0.5rem 0.75rem; }

.badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.badge-active, .badge-success, .badge-running { background: rgba(34, 197, 94, 0.2