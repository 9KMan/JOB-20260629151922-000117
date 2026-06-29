README.md
# Business Process Automation — Web Scraping + Data Pipeline (MVP)

**Project ID:** JOB-20260629151922-000117
**Upwork:** https://www.upwork.com/jobs/~022071567341570058217
**Stack:** Python 3.12 + Playwright + FastAPI + PostgreSQL + APScheduler + Telegram Bot API + Docker
**Architecture:** ETL pipeline with idempotent fetches, retry queues, dead-letter handling

---

## Business Problem Solved

Manual copy-paste from 2-3 websites into spreadsheets is unreliable, slow, and unscalable. We replace it with an automated pipeline that:

1. **Scrapes** business data from target sites using Playwright (modern Chromium-based, headless)
2. **Cleans** the raw HTML into structured records (Pydantic-validated)
3. **Stores** records in PostgreSQL for history and deduplication
4. **Delivers** results as CSV exports + Google Sheets (via API) + Telegram summary
5. **Runs automatically** on cron schedule with retry/DLQ safety nets

Goal: a clean MVP that the operator can extend later — no over-engineering, no Kubernetes, no microservices.

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Scrape 2-3 configurable target sites via Playwright | Must |
| FR-2 | Parse raw HTML into normalized Pydantic records | Must |
| FR-3 | Store records in PostgreSQL with upsert dedup | Must |
| FR-4 | Export to CSV (one-click download) | Must |
| FR-5 | Export to Google Sheets (auto-update) | Should |
| FR-6 | Cron-scheduled pipeline (default: daily 09:00 UTC) | Must |
| FR-7 | Retry on transient failures (3x exponential backoff) | Must |
| FR-8 | Dead-letter queue for permanent failures + alert | Must |
| FR-9 | Optional Telegram bot: ping on completion/failure | Should |
| FR-10 | Configuration via YAML (no code change for new sites) | Must |
| FR-11 | Health-check endpoint `/health` | Must |
| FR-12 | Operator CLI for manual runs (`python -m pipeline.cli`) | Should |

---

## Non-Functional Requirements

- **Reliability:** 99% run success rate over 30 days; permanent failure alerts within 5 min
- **Idempotency:** Re-running a scrape produces the same result set (no duplicates)
- **Observability:** Structured JSON logs (loguru), run history table, last-24h dashboard
- **Security:** Credentials in env vars (never in code), CSRF on admin endpoints, Telegram bot token in env
- **Maintainability:** Add a new target site via YAML config + one selector map (no Python edits)
- **Performance:** Scrape 1000 records from a typical directory site in <10 min

---

## Constraints

- **MVP scope:** Clean, extensible. Not heavy system design. Not scaling-ready (single-host deployment).
- **Stack:** Selenium OR Playwright (we prefer Playwright — faster, less flaky).
- **Delivery format:** CSV (mandatory) + Google Sheets (optional) + Telegram summary (optional).
- **Backend experience:** "useful" — implies Python-leaning, not just frontend.
- **Storage:** PostgreSQL is optional ("for storage or logging setup"). If used → `fastapi-postgres-crud` base template.

---

## Technical Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Scraper | Playwright (Python sync API) | Faster + more reliable than Selenium for modern SPAs |
| HTTP fallback | httpx + selectolax | Pure-server-rendered sites don't need a browser |
| Validation | Pydantic v2 | Type-safe records, JSON Schema export for Sheets |
| API | FastAPI + Uvicorn | Admin endpoints + `/health` + CSV export |
| DB | PostgreSQL 15 + SQLAlchemy | Persistent history, idempotent upserts |
| Scheduler | APScheduler (in-process) | Simpler than Celery for single-host MVP |
| Bot | python-telegram-bot (v20) | Async-native, well-maintained |
| Sheets | gspread + service account | Standard library, OAuth service-account flow |
| Packaging | uv + Dockerfile | Reproducible builds, one-command boot |
| Testing | pytest + pytest-asyncio | Standard for async FastAPI work |
| Logs | loguru | JSON-formatted, file rotation, Telegram hook |

---

## Architecture

