## Phase Goal
Design and document the system architecture for the web scraping + data pipeline MVP, defining API contracts, data flow, module boundaries, and integration points across Playwright scrapers, FastAPI service, PostgreSQL persistence, and Telegram/Sheets delivery.

## Files to Create

```file:docs/architecture/01-overview.md
# Architecture Overview

## System Context

```
+------------------+        +-------------------+        +-----------------+
|   Target Sites   |  HTTP  |  Scraper Service  |  ETL   |   PostgreSQL    |
|   (3rd party)    |<------>|  (Playwright)     |------->|   (records)     |
+------------------+        +-------------------+        +-----------------+
                                     |                            |
                                     | API                        | SQL
                                     v                            v
                            +-------------------+        +-----------------+
                            |  FastAPI Service  |<------>|   Scheduler     |
                            |  (REST + tasks)   |        |   (APScheduler) |
                            +-------------------+        +-----------------+
                                     |
                          +----------+-----------+
                          |          |           |
                          v          v           v
                    +---------+ +---------+ +---------+
                    |  CSV    | | Sheets  | | Telegram|
                    | Export  | | API     | | Bot     |
                    +---------+ +---------+ +---------+
```

## Architectural Style
- **ETL pipeline** with strict stage boundaries: Extract (Playwright) -> Transform (Pydantic) -> Load (SQLAlchemy).
- **Service-oriented** internal layout: scraper, api, scheduler, notifier as separate modules in a monorepo.
- **Idempotent operations**: every fetch keyed by `source_id` + `external_id`; every load uses `ON CONFLICT DO UPDATE`.

## Key Design Principles
1. **Async-first** — all I/O uses asyncio (asyncpg, httpx, Playwright async API, APScheduler AsyncIOScheduler).
2. **Single writer per record** — scraper and API never both mutate the same row; concurrency controlled by DB-level upsert.
3. **Configuration externalized** — no secrets in code; env-driven via pydantic-settings.
4. **Observable by default** — structured logs with `request_id` propagated end-to-end.
5. **Graceful degradation** — Telegram/Sheets failures never block the core ETL path.

## Component Inventory
| Component | Responsibility | Tech |
|-----------|---------------|------|
| `scraper/` | Browser automation, page parsing | Playwright (async) |
| `pipeline/` | Orchestration of ETL stages | asyncio, APScheduler |
| `api/` | HTTP surface for operators | FastAPI, Uvicorn |
| `db/` | Persistence, migrations | SQLAlchemy 2.0 async, Alembic |
| `delivery/` | CSV/Sheets/Telegram export | httpx, gspread, python-telegram-bot |
| `core/` | Settings, logging, errors | pydantic-settings, structlog |

## Deployment Topology
- Single Docker container for MVP; services run as async tasks within one process boundary.
- PostgreSQL is external (managed or sidecar).
- Future: split scraper/api into separate containers behind a shared DB.
```

```file:docs/architecture/02-data-flow.md
# Data Flow

## End-to-End Record Lifecycle

```
1. TRIGGER
   Cron tick (APScheduler) OR manual POST /scrape
        |
        v
2. EXTRACT
   Playwright launches headless Chromium
   -> navigates to source URL
   -> waits for selector (data-ready signal)
   -> returns raw HTML / DOM snapshot
        |
        v
3. TRANSFORM
   Parser extracts fields (BeautifulSoup or Playwright locators)
   -> constructs Pydantic SourceRecord
   -> validation errors logged + routed to DLQ
        |
        v
4. LOAD
   SQLAlchemy upsert into `records` table
   ON CONFLICT (source_id, external_id) DO UPDATE
        |
        v
5. NOTIFY (best-effort)
   If new/changed -> queue Telegram message
   If configured -> append to Google Sheet
   If scheduled -> write CSV to /exports
        |
        v
6. AUDIT
   Insert row into `scrape_runs` with counts + status
```

## Data Flow Invariants
- A record is **never deleted** by the pipeline; status transitions only (`active` -> `stale`).
- Every run produces **exactly one** `scrape_runs` row, even on failure.
- Transform failures do **not** abort the run; they append to a `parse_failures` table for reprocessing.

## State Machines

### ScrapeRun
```
scheduled -> running -> (succeeded | partial | failed)
                          |              |
                          v              v
                       notified       dead_lettered
```

### RecordStatus
```
new -> active -> (updated | stale | removed)
```

## Backpressure
- Single concurrent browser context per process (Playwright BrowserContext is heavy).
- `asyncio.Semaphore(1)` wraps Playwright calls to enforce serial extraction.
- Transform + load remain concurrent (CPU/IO light).

## Idempotency Keys
- Primary key: `(source_id, external_id)` — supplied by source, not generated.
- Run key: `run_id` (UUIDv4) — generated at trigger time, logged in every stage.
```

```file:docs/architecture/03-api-contract.md
# API Contract

Base URL: `http://<host>:8000`
OpenAPI/Swagger: `http://<host>:8000/docs`
Content-Type: `application/json` (except CSV exports)

## Endpoints

### `GET /health`
Liveness probe.
**Response 200:**
```json
{"status": "ok", "version": "0.1.0", "db": "ok"}
```

### `GET /ready`
Readiness probe (verifies DB + browser binary present).
**Response 200:** `{"ready": true}`
**Response 503:** `{"ready": false, "checks": {"db": "ok", "chromium": "missing"}}`

### `POST /scrape`
Trigger an immediate scrape run for one source.
**Request:**
```json
{"source_id": "site_a", "force_full": false}
```
**Response 202:**
```json
{"run_id": "uuid", "status": "scheduled"}
```

### `GET /runs`
Paginated list of scrape runs.
**Query:** `?limit=20&offset=0&source_id=site_a&status=succeeded`
**Response 200:**
```json
{"items": [...], "total": 42, "limit": 20, "offset": 0}
```

### `GET /runs/{run_id}`
Fetch single run with counts and error summary.
**Response 200:**
```json
{"run_id": "uuid", "source_id": "site_a", "started_at": "...", "finished_at": "...",
 "status": "succeeded", "records_extracted": 150, "records_loaded": 148,
 "records_failed": 2, "errors": [...]}
```

### `GET /records`
Query the canonical record store.
**Query:** `?source_id=site_a&status=active&updated_after=2026-01-01T00:00:00Z&limit=50`
**Response 200:**
```json
{"items": [...], "total": 1234, "limit": 50, "offset": 0}
```

### `GET /exports/csv`
Stream a CSV export of current records.
**Query:** `?source_id=site_a&status=active`
**Response 200:** `text/csv` attachment

### `GET /sources`
List configured scrape sources.
**Response 200:**
```json
{"items": [{"source_id": "site_a", "url": "...", "schedule": "0 * * * *", "enabled": true}]}
```

## Error Format
All non-2xx responses use:
```json
{"error": {"code": "validation_error", "message": "...", "details": {...}}}
```

Standard codes: `400 validation_error`, `404 not_found`, `409 conflict`, `500 internal_error`.

## Auth
MVP: bearer token via `Authorization: Bearer <token>` from `API_TOKEN` env var. No per-user auth.
```

```file:docs/architecture/04-database-schema.md
# Database Schema (PostgreSQL 15+)

## Tables

### `sources`
Configuration for each scrape target.
| Column | Type | Notes |
|--------|------|-------|
| source_id | text PK | logical id, e.g. `site_a` |
| display_name | text NOT NULL | |
| base_url | text NOT NULL | |
| schedule_cron | text NOT NULL | APScheduler-compatible |
| enabled | boolean NOT NULL DEFAULT true | |
| parser_module | text NOT NULL | dotted path to parser class |
| selectors_json | jsonb NOT NULL | CSS selectors, timeouts |
| created_at | timestamptz NOT NULL DEFAULT now() | |
| updated_at | timestamptz NOT NULL DEFAULT now() | |

### `records`
Canonical scraped records.
| Column | Type | Notes |
|--------|------|-------|
| id | bigserial PK | |
| source_id | text NOT NULL, FK -> sources | |
| external_id | text NOT NULL | from source site |
| payload | jsonb NOT NULL | structured fields |
| raw_hash | text NOT NULL | sha256 of normalized payload |
| status | text NOT NULL | `new`/`active`/`stale`/`removed` |
| first_seen_at | timestamptz NOT NULL | |
| last_seen_at | timestamptz NOT NULL | |
| updated_at | timestamptz NOT NULL | |
| UNIQUE | (source_id, external_id) | |

### `scrape_runs`
Audit log of each pipeline execution.
| Column | Type | Notes |
|--------|------|-------|
| run_id | uuid PK | |
| source_id | text NOT NULL | |
| trigger | text NOT NULL | `cron`/`manual`/`retry` |
| started_at | timestamptz NOT NULL | |
| finished_at | timestamptz | nullable while running |
| status | text NOT NULL | `running`/`succeeded`/`partial`/`failed` |
| records_extracted | integer NOT NULL DEFAULT 0 | |
| records_loaded | integer NOT NULL DEFAULT 0 | |
| records_failed | integer NOT NULL DEFAULT 0 | |
| error_summary | jsonb | nullable |

### `parse_failures` (DLQ)
Records that failed validation/transform.
| Column | Type | Notes |
|--------|------|-------|
| id | bigserial PK | |
| run_id | uuid NOT NULL, FK -> scrape_runs | |
| source_id | text NOT NULL | |
| external_id | text | nullable if extraction failed early |
| raw_payload | text | original HTML/JSON |
| error_message | text NOT NULL | |
| error_class | text NOT NULL | |
| retry_count | integer NOT NULL DEFAULT 0 | |
| resolved | boolean NOT NULL DEFAULT false | |
| created_at | timestamptz NOT NULL DEFAULT now() | |

### `delivery_log`
Notification/audit trail.
| Column | Type | Notes |
|--------|------|-------|
| id | bigserial PK | |
| run_id | uuid NOT NULL | |
| channel | text NOT NULL | `telegram`/`sheets`/`csv` |
| status | text NOT NULL | `sent`/`failed`/`skipped` |
| detail | jsonb | |
| created_at | timestamptz NOT NULL DEFAULT now() | |

## Indexes
- `records (source_id, status, updated_at DESC)` — primary query pattern
- `records USING GIN (payload jsonb_path_ops)` — payload search
- `scrape_runs (source_id, started_at DESC)`
- `parse_failures (resolved, created_at) WHERE NOT resolved`

## Migration Strategy
- Alembic under `db/migrations/`.
- One revision per schema change; no destructive changes without a paired downgrade.
- All timestamps stored as `timestamptz` in UTC.
```

```file:docs/architecture/05-integrations.md
# Integrations

## Playwright (scraper)
- Channel: `chromium` only for MVP.
- Launch: `playwright.async_api.async_playwright()` with `headless=True`, `args=["--no-sandbox"]` for containers.
- Lifecycle: one `Browser` instance per process, fresh `BrowserContext` per source per run.
- Network interception: block `image`, `font`, `media` resource types to reduce bandwidth.
- Selector waiting: use `page.wait_for_selector(sel, timeout=10_000)`; never `time.sleep`.

## PostgreSQL
- Driver: `asyncpg` (via SQLAlchemy 2.0 async engine).
- Pool: `pool_size=5, max_overflow=10, pool_pre_ping=True`.
- DSN: `postgresql+asyncpg://user:pass@host:5432/dbname`.
- Migrations: `alembic upgrade head` on container start, gated by `RUN_MIGRATIONS=true`.

## APScheduler
- Scheduler: `AsyncIOScheduler`, single instance, runs in the FastAPI event loop.
- Job store: `MemoryJobStore` (MVP); switch to `SQLAlchemyJobStore` if multi-instance.
- Misfire grace: 60s; coalesce: true.
- Jobs registered at startup from `sources.schedule_cron`.

## Telegram Bot API
- Library: `python-telegram-bot` v21+ (async).
- Mode: bot sends messages to a configured chat id; no inbound commands in MVP.
- Throttling: max 1 message per second per chat; queue via `asyncio.Queue` with worker.
- Failure handling: HTTP 429 respected via `Retry-After`; other failures logged + retried 3x then dropped to `delivery_log` as `failed`.

## Google Sheets (optional)
- Library: `gspread` + service account JSON.
- Auth: `GOOGLE_SERVICE_ACCOUNT_JSON` env var (path) or inline JSON.
- Strategy: append-only to a configured sheet id; header row written on first run.
- Failures: never block ETL; logged to `delivery_log`.

## CSV Export
- Stdlib `csv` module, written to `/exports/{source_id}_{utc_timestamp}.csv`.
- Streamed via FastAPI `StreamingResponse` for `GET /exports/csv`.
- No external dependency.

## Observability
- Logs: `structlog` JSON output to stdout (container-friendly).
- Correlation: `request_id` header on API -> injected into `run_id` for manual triggers -> logged at every stage.
- Metrics (out of scope for MVP, but ready): `prometheus_client` middleware stub.
```

```file:docs/architecture/06-module-layout.md
# Module Layout

```
app/
├── __init__.py
├── main.py                  # FastAPI app factory + lifespan
├── core/
│   ├── __init__.py
│   ├── config.py            # pydantic-settings Settings
│   ├── logging.py           # structlog setup
│   └── errors.py            # AppError taxonomy
├── db/
│   ├── __init__.py
│   ├── engine.py            # async engine + session factory
│   ├── models.py            # SQLAlchemy ORM models
│   └── migrations/           # Alembic
│       ├── env.py
│       └── versions/
├── api/
│   ├── __init__.py
│   ├── deps.py              # DI: db session, current settings
│   ├── routes/
│   │   ├── health.py
│   │   ├── runs.py
│   │   ├── records.py
│   │   ├── sources.py
│   │   └── exports.py
│   └── schemas/             # Pydantic request/response models
│       ├── runs.py
│       ├── records.py
│       └── sources.py
├── scraper/
│   ├── __init__.py
│   ├── browser.py           # Playwright lifecycle
│   ├── base.py              # BaseScraper abstract class
│   └── parsers/
│       ├── site_a.py
│       └── site_b.py
├── pipeline/
│   ├── __init__.py
│   ├── orchestrator.py      # RunPipeline.run(source_id)
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── scheduler/
│   ├── __init__.py
│   └── jobs.py              # APScheduler registration
└── delivery/
    ├── __init__.py
    ├── telegram.py
    ├── sheets.py
    └── csv_export.py
tests/
├── unit/
├── integration/
└── fixtures/
docker/
├── Dockerfile
└── docker-compose.yml       # app + postgres
pyproject.toml
alembic.ini
.env.example
```

## Dependency Direction
- `api/` -> `pipeline/` -> `scraper/`, `db/`, `delivery/`
- `core/` is leaf (no inbound dependencies from business modules).
- `db/` is leaf (ORM models only; no business logic).
- No circular imports; `__init__.py` files are empty except where re-exports are explicit.

## Async Boundaries
- All public functions in `scraper/`, `pipeline/`, `delivery/telegram.py` are `async def`.
- Sync helpers (CSV writing, JSON parsing) wrapped with `asyncio.to_thread` only when blocking > 5ms.
```

```file:docs/architecture/07-deployment.md
# Deployment

## Container Layout
- Base image: `python:3.12-slim`.
- Playwright deps installed via `mcr.microsoft.com/playwright/python:v1.45.0-jammy` (or official install script).
- Non-root user `app` (uid 1000).
- Entrypoint: `python -m app.main` (Uvicorn launched in-process, not via CLI, to share event loop with scheduler).

## Environment Variables (see `.env.example`)
```
DATABASE_URL=postgresql+asyncpg://app:app@db:5432/pipeline
API_TOKEN=change-me
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
GOOGLE_SERVICE_ACCOUNT_JSON=
RUN_MIGRATIONS=true
LOG_LEVEL=INFO
```

## Health & Restart
- `GET /health` returns 200 when process is up.
- `GET /ready` returns 200 only when DB is reachable and Playwright browser binary is installed.
- Docker `HEALTHCHECK` uses `/health` every 30s; `restart: unless-stopped`.

## Startup Sequence
1. Load settings.
2. Configure structured logging.
3. If `RUN_MIGRATIONS=true`: `alembic upgrade head`.
4. Initialize Playwright browser (lazy; first scrape).
5. Start `AsyncIOScheduler`, register jobs from `sources`.
6. Start Uvicorn on `0.0.0.0:8000`.

## Scaling Notes (out of MVP scope)
- Scraping is intentionally single-instance due to APScheduler MemoryJobStore.
- API and DB tiers scale independently once split.
- DLQ table enables deferred batch reprocessing without holding the hot path.
```

## Done When
- All 7 architecture documents exist under `docs/architecture/` with the exact filenames listed above.
- `docs/architecture/03-api-contract.md` enumerates endpoints matching the SPEC (health, scrape, runs, records, exports, sources) with request/response JSON shapes.
- `docs/architecture/04-database-schema.md` defines tables `sources`, `records`, `scrape_runs`, `parse_failures`, `delivery_log` with the specified columns, types, and uniqueness constraint on `(source_id, external_id)`.
- `docs/architecture/06-module-layout.md` shows an `app/` tree that includes `core/`, `db/`, `api/`, `scraper/`, `pipeline/`, `scheduler/`, `delivery/` subpackages.
- An architecture review command passes: `python -c "import pathlib; [print(p) for p in sorted(pathlib.Path('docs/architecture').glob('*.md'))]"` prints exactly 7 files (01-overview through 07-deployment).

## Acceptance Notes
- This phase delivers the **blueprint** that Phase 4 (Implementation) builds against; no production code runs yet, but every later file has a documented home.
- Supports the **ETL pipeline + idempotent fetches + retry queues + dead-letter handling** architecture called out in SPEC.md by explicitly modeling `scrape_runs`, `parse_failures` (DLQ), and `ON CONFLICT` upsert semantics.
- Reflects the detected **Python + PostgreSQL** stack constraint from CONTEXT.md and the RESEARCH.md decisions (Playwright chromium, FastAPI, SQLAlchemy 2.0 async + asyncpg, APScheduler, httpx).
- Provides the API surface the operator needs to trigger, monitor, and export scrapes without direct DB access, addressing the "delivery as CSV exports + Google Sheets + Telegram summary" goal from SPEC.md.
- Defines integration boundaries (Playwright lifecycle, Telegram throttling, Sheets best-effort) so Phase 4 implementation can proceed in parallel tracks without architectural ambiguity.