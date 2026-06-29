# Business Process Automation — Web Scraping + Data Pipeline (MVP)

Automated ETL pipeline that scrapes business data from 2–3 target sites, normalizes
records via Pydantic, persists them to PostgreSQL, and delivers results through
CSV export, Google Sheets, and Telegram — all on a cron schedule with retries and
a dead-letter queue.

---

## Documentation

- [Project Overview](docs/PROJECT_OVERVIEW.md) — purpose, scope, architecture, risks
- [Glossary](docs/GLOSSARY.md) — shared vocabulary
- [Phase Log](docs/PHASE_LOG.md) — phase-by-phase delivery record

## Stack

- **Language:** Python 3.12
- **Scraping:** Playwright (headless Chromium) + httpx fallback
- **Validation:** Pydantic v2
- **API:** FastAPI + Uvicorn
- **DB:** PostgreSQL 15 + SQLAlchemy 2.0 (async) + asyncpg
- **Scheduler:** APScheduler (CronTrigger)
- **Delivery:** CSV, Google Sheets API, Telegram Bot API
- **Packaging:** uv + Docker + docker compose

## Quick Start

