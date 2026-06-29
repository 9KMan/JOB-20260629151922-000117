# Business Process Automation — Web Scraping + Data Pipeline (MVP)

**Job ID:** JOB-20260629151922-000117

Automated ETL pipeline that scrapes 2–3 target sites with Playwright, validates
records with Pydantic, stores them in PostgreSQL with idempotent dedup, and
delivers results as CSV + Google Sheets + Telegram digest.

---

## Documentation

| Document | Purpose |
|----------|---------|
| [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) | Scope, success criteria, architecture, phase map |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Shared vocabulary |
| [docs/PHASE_LOG.md](docs/PHASE_LOG.md) | Phase-by-phase progress and deliverable log |

---

## Stack (Quick View)

Python 3.12 · Playwright · FastAPI · PostgreSQL 15 · APScheduler · Telegram Bot API · Docker

---

## Status

**Phase 1 — Project Overview:** Complete (see [docs/PHASE_LOG.md](docs/PHASE_LOG.md))
