cat > README.md << 'MDEOF'
# Business Process Automation — Web Scraping + Data Pipeline (MVP)

Automated ETL pipeline that replaces manual copy-paste workflows from 2–3 target websites with scheduled scraping, validation, persistence, and multi-channel delivery (CSV, Google Sheets, Telegram).

**Project ID:** JOB-20260629151922-000117
**Stack:** Python 3.12 · Playwright · FastAPI · PostgreSQL · APScheduler · Telegram Bot API · Docker

---

## Quick Links

- **Full scope, architecture, and phase map:** [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md)
- **Shared vocabulary:** [`docs/GLOSSARY.md`](docs/GLOSSARY.md)
- **Phase progress:** [`docs/PHASE_LOG.md`](docs/PHASE_LOG.md)

---

## What this project does

| Stage | Component | Output |
|-------|-----------|--------|
| Extract | Playwright (headless Chromium) + httpx fallback | Raw HTML / JSON |
| Transform | Pydantic v2 normalizer | Validated records |
| Load | SQLAlchemy 2.0 (async) + asyncpg into PostgreSQL | Idempotent rows |
| Deliver | CSV writer · Google Sheets client · Telegram Bot | Operator-facing artifacts |
| Schedule | APScheduler (CronTrigger) with SQLAlchemy jobstore | Daily 09:00 UTC default |

Key guarantees: **idempotent fetches**, **exponential-backoff retries**, **dead-letter queue**, **health-checked** FastAPI service, **single-command Docker deployment**.

---

## Architecture (at a glance)

