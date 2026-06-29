# Business Process Automation — Web Scraping + Data Pipeline (MVP)

Automated ETL pipeline that scrapes business data from configured target sites,
normalizes it through Pydantic validation, persists it to PostgreSQL with
idempotent dedup, and delivers results via CSV export, Google Sheets, and
Telegram — all on a cron schedule with retry and dead-letter handling.

**Project ID:** JOB-20260629151922-000117
**Status:** MVP (in active development)

---

## Quick Links

- [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) — full scope, success
  criteria, architecture, risks, phase map
- [docs/GLOSSARY.md](docs/GLOSSARY.md) — shared vocabulary for downstream phases
- [docs/PHASE_LOG.md](docs/PHASE_LOG.md) — completed phase records

---

## Stack at a Glance

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| Browser automation | Playwright (chromium) |
| Web framework | FastAPI + Uvicorn |
| ORM / DB driver | SQLAlchemy 2.0 (async) + asyncpg |
| Validation | Pydantic v2 |
| Scheduler | APScheduler (CronTrigger) |
| Database | PostgreSQL 15 |
| Delivery | CSV, Google Sheets (gspread), Telegram Bot API |
| HTTP client | httpx |
| Container | Docker + docker compose |

---

## What This Project Does

1. **Schedules** scrapes via APScheduler on a configurable cron (default: daily
   09:00 UTC).
2. **Fetches** target pages with Playwright (or httpx for static endpoints).
3. **Parses** the DOM through configurable selector maps into Pydantic records.
4. **Stores** records in PostgreSQL using an upsert keyed on
   `(target_id, external_id)` so re-runs are idempotent.
5. **Retries** transient failures with exponential backoff (3 attempts by
   default); permanent failures land in a dead-letter queue (DLQ) table.
6. **Delivers** results to operators as CSV downloads, optional Google Sheets
   updates, and an optional Telegram summary message.
7. **Exposes** FastAPI endpoints (`/health`, `/status`, `/dlq`) for operator
   visibility and operator CLI manual runs.

---

## Repository Layout (planned)

