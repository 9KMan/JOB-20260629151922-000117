# Business Process Automation — Web Scraping + Data Pipeline (MVP)

> > # SPEC: Business Process Automation — Web Scraping + Data Pipeline (MVP)

**Job:** JOB-20260629151922-000117
**Upwork:** https://www.

**Built by: KMan | AI-Augmented Engineering Factory**

---

## Business Problem Solved

# SPEC: Business Process Automation — Web Scraping + Data Pipeline (MVP)

**Job:** JOB-20260629151922-000117
**Upwork:** https://www.upwork.com/jobs/~022071567341570058217
**Stack:** Python 3.12 + Playwright + FastAPI + PostgreSQL + APScheduler + Telegram Bot API + Docker
**Architecture:** ETL pipeline with idempotent fetches, retry queues, dead-letter handling

---

## 1. Business Problem Solved

Manual copy-paste from 2-3 websites into spreadsheets is unreliable, slow, and unscalable. We replace it with an automated pipeline that:

1. **Scrapes** business data from target sites using Playwright (modern Chromium-based, headless)
2. **Cleans** the raw HTML into structured records (Pydantic-validated)
3. **Stores** records in PostgreSQL for history and deduplication
4. **Delivers** results as CSV exports + Google Sheets (via API) + Telegram summary
5. **Runs automatically** on cron schedule with retry/DLQ safety nets

Goal: a clean MVP that the operator can extend later — no over-engineering, no Kubernetes, no microservices.

---

## 2. Functional Requirements

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

## 3. Non-Functional Requirements

- **Reliability:** 99% run success rate over 30 days; permanent failure alerts within 5 min
- **Idempotency:** Re-running a scrape produces the same result set (no duplicates)
- **Observability:** Structured JSON logs (loguru), run history table, last-24h dashboard
- **Security:** Credentials in env vars (never in code), CSRF on admin endpoints, Telegram bot token in env
- **Maintainability:** Add a new target site via YAML config + one selector map (no Python edits)
- **Performance:** Scrape 1000 records from a typical directory site in <10 min

---

## 4. Constraints

- **MVP scope:** Clean, extensible. Not heavy system design. Not scaling-ready (single-host deployment).
- **Stack:** Selenium OR Playwright (we prefer Playwright — faster, less flaky).
- **Delivery format:** CSV (mandatory) + Google Sheets (optional) + Telegram summary (optional).
- **Backend experience:** "useful" — implies Python-leaning, not just frontend.
- **Storage:** PostgreSQL is optional ("for storage or logging setup"). If used → `fastapi-postgres-crud` base template.

---

## 5. Technical Stack

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

## 6. Architecture

```
┌──────────────┐
│  Schedule    │  APScheduler (cron "0 9 * * *")
│  (daily 09u) │
└──────┬───────┘
       │ trigger
       ▼
┌──────────────┐    ┌─────────────────┐
│  Pipeline    │───▶│  Playwright      │  (or httpx for static sites)
│  Orchestrator│    │  Scraper Worker  │
└──────┬───────┘    └────────┬────────┘
       │                     │
       │                     ▼
       │            ┌─────────────────┐
       │            │ Pydantic Parser │
       │            │ + Normalizer    │
       │            └────────┬────────┘
       │                     │
       │                     ▼
       │            ┌─────────────────┐
       │            │ PostgreSQL     │  (record store + idempotent upsert)
       │            │ (records table)│
       │            └────────┬────────┘
       │                     │
       ├─────────────────────┤
       │                     │
       ▼                     ▼
┌──────────────┐    ┌─────────────────┐
│  Failure     │    │  Output         │
│  → DLQ       │    │  • CSV export   │
│  → Telegram  │    │  • Google Sheets│
└──────────────┘    │  • CLI download │
                    └─────────────────┘
```

---

## 7. Data Model

### `scraper_targets` (config table)
```sql
id            SERIAL PK
name          TEXT UNIQUE
url           TEXT
selector_map  JSONB       -- {"row": ".item", "name": "h2", "phone": ".tel"}
schedule      TEXT        -- cron expression (default: "0 9 * * *")
enabled       BOOLEAN DEFAULT true
created_at    TIMESTAMPTZ
```

### `records` (scraped data)
```sql
id              BIGSERIAL PK
target_id       INT FK -> scraper_targets
external_id     TEXT             -- dedup key from source
payload         JSONB            -- normalized record
source_url      TEXT             -- verify-link back to source
scraped_at      TIMESTAMPTZ
UNIQUE(target_id, external_id)   -- idempotency
```

### `runs` (execution history)
```sql
id              SERIAL PK
target_id       INT FK
started_at      TIMESTAMPTZ
finished_at     TIMESTAMPTZ
status          TEXT            -- 'success'|'partial'|'failed'
records_new     INT
records_updated INT
error_message   TEXT
```

---

## 8. Directory Structure

```
scrape-pipeline/
├── README.md
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── pipeline/
│   ├── __init__.py
│   ├── cli.py              # `python -m pipeline.cli run --target acme`
│   ├── orchestrator.py     # APScheduler + run orchestration
│   ├── scrapers/
│   │   ├── base.py         # PlaywrightScraper abstract
│   │   ├── playwright.py   # browser-based scraper
│   │   └── http.py         # httpx + selectolax fallback
│   ├── parsers/
│   │   ├── normalize.py    # text/coerce helpers
│   │   └── validate.py     # Pydantic schemas per target
│   ├── db/
│   │   ├── models.py
│   │   ├── schema.sql
│   │   └── upsert.py       # idempotent insert
│   ├── schedulers/
│   │   └── cron.py         # APScheduler config
│   ├── outputs/
│   │   ├── csv_export.py
│   │   ├── sheets.py       # Google Sheets via gspread
│   │   └── telegram.py     # bot notifier
│   ├── retry.py            # tenacity-backed retry
│   └── dlq.py              # dead-letter queue
├── config/
│   └── targets.yaml        # editable site configs
├── tests/
│   ├── test_parsers.py
│   ├── test_upsert.py
│   ├── test_retry.py
│   └── fixtures/
└── docs/
    ├── architecture.md
    ├── adding-a-target.md
    └── deployment.md
```

---

## 9. Acceptance Criteria

- [ ] `docker-compose up` boots API + Postgres + scheduler in <30s
- [ ] Two target sites configured in `config/targets.yaml`
- [ ] Manual scrape via `python -m pipeline.cli run --target <name>` produces CSV
- [ ] Auto-scrape on cron produces CSV + updates Sheets + sends Telegram summary
- [ ] Scraping a duplicate record updates the existing row, not insert (verify in DB)
- [ ] Transient failure (network timeout) retries 3x with backoff
- [ ] Permanent failure routes to DLQ table + Telegram alert
- [ ] Adding a third target requires only YAML config + one selector map (no Python edits)
- [ ] All tests pass (`pytest -q`): ≥ 20 tests
- [ ] README documents: Quick Start, Architecture diagram, How to add a target, Deployment

---

## 10. Out of Scope

- Horizontal scaling (single-host MVP)
- Kubernetes / helm charts
- Multi-tenant isolation
- Distributed task queue (Celery/Redis) — APScheduler in-process is fine for this scale
- Per-site proxy rotation (assume sites are friendly; add later if needed)
- CAPTCHA solving
- Web UI dashboard — we use Telegram summaries + DB queries for status

---

## 11. Deployment

- **Local dev:** `uv run python -m pipeline.cli run --target acme`
- **Production:** `docker-compose up -d` on a single VPS
- **Logs:** `loguru` JSON to stdout + `/var/log/scrape/`
- **Health:** `GET http://host:8000/health` → 200 OK with `{"status": "ok", "last_run": "..."}`

---

## 12. References

- `references/scraper_target_template.md` — YAML schema for new targets
- `references/troubleshooting_selenium_to_playwright.md` — common migration pitfalls
- `references/google_sheets_service_account_setup.md` — OAuth flow
- `references/telegram_bot_token_setup.md` — bot registration


---

## Scope

# SPEC: Business Process Automation — Web Scraping + Data Pipeline (MVP)

**Job:** JOB-20260629151922-000117
**Upwork:** https://www. upwork. com/jobs/~022071567341570058217
**Stack:** Python 3.

---

## 🏗 Technical Stack

_Not specified — see SPEC.md for full tech stack._

---

## Architecture

<p align="center">
  <img src="./diagrams/architecture.svg" alt="Architecture Diagram" width="900"/>
</p>

_Local view: `xdg-open diagrams/architecture.svg`_

---

## ✅ Acceptance Criteria

1. **Working application** — builds and runs without errors
2. **Tests** — pytest with ≥5 passing tests
3. **Docker** — `docker compose up --build` succeeds
4. **README** — complete run instructions and feature documentation

---

## 🚀 Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/9KMan/JOB-20260629151922-000117 && cd $(basename "https://github.com/9KMan/JOB-20260629151922-000117" .git)

# 2. Configure environment
cp .env.example .env
# Edit .env — set required environment variables

# 3. Start everything
docker compose up --build

# 4. Verify
curl http://localhost:8000/api/v1/health/
# → {"status":"ok","database":"connected"}
```

---

## 📦 What's in this repo

- `SPEC.md` — full job specification (source of truth)
- `PROPOSAL.md` — client-facing proposal
- `COVER_LETTER.txt` — cover letter for bid submission
- `ROADMAP.md` — phased delivery plan
- `CLAUDE.md` — operating notes for AI build workers
- `src/bpa/` — application source (FastAPI + Playwright/httpx scrapers + ETL pipeline)
- `tests/` — 48 pytest tests covering parsers, retry, dlq, settings, pipeline
- `config/targets.yaml` — sample target site configurations
- `diagrams/architecture.svg` — stack-adaptive system architecture diagram
- `Dockerfile`, `docker-compose.yml` — one-command boot
- `requirements.txt` — pinned Python dependencies
- `.env.example` — environment variable template
