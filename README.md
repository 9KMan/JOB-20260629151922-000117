# Business Process Automation — Web Scraping + Data Pipeline (MVP)

Automated ETL pipeline that scrapes business data from 2–3 configurable websites,
normalizes records with Pydantic v2, persists to PostgreSQL with idempotent
deduplication, and delivers results via CSV export, Google Sheets, and a
Telegram bot. Runs on a cron schedule with retry + dead-letter queue safety nets.

---

## Status

**Phase:** 1 — Project Overview (Complete)
**Project ID:** JOB-20260629151922-000117
**Stack:** Python 3.12 · Playwright · FastAPI · PostgreSQL 15 · APScheduler · Docker
**Spec:** see [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md)

---

## Repository Layout

