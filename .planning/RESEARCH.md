# RESEARCH.md

## Tech Stack Decisions

### Web Scraping: Playwright (already specified)
**Decision:** Confirm Playwright with chromium channel
**Justification:** Modern async-capable browser automation with built-in waiting, network interception, and headless mode. Superior to Selenium for Python 3.12+ due to native async support and better performance.

### Web Framework: FastAPI (already specified)
**Decision:** FastAPI + Uvicorn
**Justification:** Native async/await, automatic OpenAPI docs, Pydantic integration, and ASGI performance. Coroutines enable concurrent scraping requests.

### Database Access: SQLAlchemy 2.0 + asyncpg
**Decision:** SQLAlchemy 2.0 (async mode) + asyncpg driver
**Justification:** Full async PostgreSQL driver (not psycopg2), type-safe queries, Alembic migrations, and ORM flexibility for complex joins vs raw SQL simplicity.

### ORM Strategy: Pydantic v2 for domain models, SQLAlchemy for persistence
**Decision:** Dual-model approach
**Justification:** Pydantic v2 for validation/transformation (fast, typed), SQLAlchemy for DB schema/migrations. Avoids Tortoise ORM for PostgreSQL due to maturity concerns.

### Scheduling: APScheduler (already specified)
**Decision:** APScheduler with CronTrigger
**Justification:** Already specified. Lightweight, no Redis dependency. Trade-off: no distributed scheduling, acceptable for single-instance MVP.

### HTTP Client: httpx
**Decision:** httpx (async HTTP client)
**Justification:** Async-native, sync and async modes, connection pooling, retries built-in. Preferred over aiohttp for simpler API and requests-like interface.

### Retry Logic: Tenacity
**Decision:** Tenacity for retry decorators
**Justification:** Battle-tested, configurable exponential backoff, jitter, and stop conditions. Cleaner than manual retry loops.

### Telegram Bot: python-telegram-bot v20+
**Decision:** python-telegram-bot==20.x (async version)
**Justification:** Official Python library with async support, polling and webhook modes, well-documented. aiogram is an alternative but python-telegram-bot has broader community support.

### Google Sheets: google-api-python-client
**Decision:** google-api-python-client + google-auth
**Justification:** Official Google client, service account auth, batch update support. Trade-off: API complexity, but required for Google Sheets integration.

### Dead Letter Queue: Custom PostgreSQL-based
**Decision:** PostgreSQL table as DLQ with status tracking
**Justification:** No Redis/Celery dependency for MVP. Single-table DLQ with `status` enum (`pending`, `processing`, `failed`, `dead_letter`) and retry count. Sufficient for single-instance operation.

---

## Library Choices

### Web & Scraping
| Package | Version | Purpose |
|---------|---------|---------|
| `playwright` | `>=1.40.0` | Browser automation, headless Chromium |
| `httpx` | `>=0.26.0` | Async HTTP client for API calls |
| `beautifulsoup4` | `>=4.12.0` | HTML parsing fallback |
| `lxml` | `>=5.0.0` | Fast XML/HTML parser (bs4 dependency) |

### Database
| Package | Version | Purpose |
|---------|---------|---------|
| `asyncpg` | `>=0.29.0` | Async PostgreSQL driver |
| `sqlalchemy` | `>=2.0.25` | ORM with async support |
| `alembic` | `>=1.13.0` | Database migrations |

### API & Validation
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | `>=0.109.0` | Web framework |
| `uvicorn` | `>=0.27.0` | ASGI server |
| `pydantic` | `>=2.5.0` | Data validation/models |
| `pydantic-settings` | `>=2.1.0` | Settings management |

### Task Scheduling & Retry
| Package | Version | Purpose |
|---------|---------|---------|
| `apscheduler` | `>=3.10.0` | Cron/scheduled jobs |
| `tenacity` | `>=8.2.0` | Retry logic with backoff |

### Integrations
| Package | Version | Purpose |
|---------|---------|---------|
| `python-telegram-bot` | `>=20.7.0` | Telegram Bot API v20+ |
| `google-api-python-client` | `>=2.100.0` | Google Sheets API |
| `google-auth` | `>=2.25.0` | Authentication |

### Export & Utilities
| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | `>=2.1.0` | CSV generation, data manipulation |
| `python-dotenv` | `>=1.0.0` | Environment variables |

### DevOps
| Package | Version | Purpose |
|---------|---------|---------|
| `psycopg2-binary` | `>=2.9.0` | psycopg for Alembic sync migrations |
| `pytest` | `>=7.4.0` | Testing |
| `pytest-asyncio` | `>=0.23.0` | Async test support |
| `docker` | `>=7.0.0` | Docker SDK (optional) |

---

## Patterns to Use

### 1. ETL Pipeline Pattern
**Implementation:** `Extractor → Transformer → Loader` classes with clear interfaces
- **Extractor:** Playwright-based scraper returning raw HTML/DOM
- **Transformer:** Pydantic-validated model conversion
- **Loader:** SQLAlchemy bulk upsert to PostgreSQL

### 2. Idempotent Fetch Pattern
**Implementation:** Primary key based on source URL + content hash
- Before scrape: check if `(source_url, content_hash)` exists
- If exists: skip or update timestamp only
- If new: proceed with ETL
- Prevents duplicate records from repeated runs

### 3. Repository Pattern
**Implementation:** `ScrapedRecordRepository` abstraction over SQLAlchemy
- `find_by_id()`, `find_by_source()`, `upsert()`, `get_failed()`
- Enables easy mocking in tests
- Can swap to different storage backend later

### 4. Dead Letter Queue Pattern
**Implementation:** Status-based tracking in PostgreSQL
```
status: Enum('pending', 'processing', 'failed', 'dead_letter')
retry_count: Integer (max 3)
last_error: Text
next_retry_at: DateTime
```
- Scheduler picks up `pending` jobs
- On failure: increment retry, set `next_retry_at`
- After 3 failures: mark `dead_letter`, alert via Telegram

### 5. Strategy Pattern for Delivery
**Implementation:** `DeliveryStrategy` interface
- `CsvDeliveryStrategy`
- `GoogleSheetsDeliveryStrategy`
- `TelegramDeliveryStrategy`
- Config-driven: select which strategies to execute per job

---

## Trade-offs Considered

### Trade-off 1: Playwright vs Scrapy vs Selenium
| Option | Pros | Cons |
|--------|------|------|
| **Playwright (chosen)** | Native async, built-in waits, modern API, fast | Larger footprint than requests+bs4 |
| Scrapy | Pure Python, lightweight, Scrapy Cloud option | No JavaScript rendering, steeper learning curve |
| Selenium | Mature, cross-browser | No async native, slow, complex setup |

**Decision:** Playwright. For MVP scraping 2-3 business sites, JavaScript rendering is likely needed for dynamic content. Async support enables concurrent scraping. Accept larger container image size.

### Trade-off 2: Celery+Redis vs Custom Retry vs Temporal/Conductor
| Option | Pros | Cons |
|--------|------|------|
| **Custom DLQ (chosen)** | No extra infrastructure, simple MVP | No distributed scheduling, manual recovery |
| Celery + Redis | Battle-tested, distributed, retry built-in | Redis dependency, operational complexity |
| Temporal | Workflow engine, durable executions | Heavy, separate service, steeper learning curve |

**Decision:** Custom PostgreSQL-based DLQ. MVP scope, single-instance operation, avoid Redis infrastructure overhead. Can migrate to Celery later if scaling requires distributed scheduling.

### Trade-off 3: pandas vs csv module for exports
| Option | Pros | Cons |
|--------|------|------|
| **pandas (chosen)** | Flexible column selection, type inference, Excel output | Heavier dependency |
| csv module | Built-in, no extra deps | Manual type handling, less feature-rich |

**Decision:** pandas. Enables easy column filtering, data type handling, and future Excel export without code changes. Worth the import overhead for a data pipeline.

---

## Confidence Assessment

| Component | Decision | Confidence | Rationale |
|-----------|----------|------------|-----------|
| Web Scraping (Playwright) | Use playwright with chromium | **HIGH** | Mature library, specified in requirements, excellent async support |
| Web Framework (FastAPI) | FastAPI + Uvicorn | **HIGH** | Production-proven, native async, Pydantic integration |
| Database (PostgreSQL) | PostgreSQL + asyncpg + SQLAlchemy 2.0 | **HIGH** | Established stack, async driver mature, relational fits ETL model |
| Scheduling (APScheduler) | APScheduler with PostgreSQL backend | **MEDIUM** | Works for single instance; no distributed scheduling; acceptable for MVP |
| Retry/DLQ | Custom PostgreSQL-based | **MEDIUM** | Simple, no extra infra; limited compared to Celery/Temporal; MVP-appropriate |
| Telegram Bot | python-telegram-bot v20 | **HIGH** | Official async library, well-documented, stable API |
| Google Sheets | google-api-python-client | **MEDIUM** | API complexity high; OAuth flow requires setup; integration reliable once configured |
| Export (CSV) | pandas | **HIGH** | Reliable, flexible, handles edge cases well |
| Idempotency | URL + content hash | **HIGH** | Standard deduplication pattern, simple to implement and test |