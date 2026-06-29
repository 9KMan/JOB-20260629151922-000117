cat > docs/GLOSSARY.md << 'MDEOF'
# Glossary

| Term | Definition |
|------|------------|
| **DLQ** | Dead-Letter Queue — table holding jobs that exhausted their retry budget |
| **ETL** | Extract, Transform, Load — the canonical pipeline pattern this project follows |
| **Idempotent fetch** | A scrape run whose repeated execution produces the same final state (no duplicates) |
| **Job** | A scheduled unit of work (one scrape window, one delivery task) |
| **Operator** | The human who monitors the pipeline and acts on Telegram alerts |
| **Poison message** | A record that fails validation repeatedly and is routed to DLQ |
| **Selector** | A Playwright/CSS/XPath locator pointing at an element on the source page |
| **Selector map** | JSONB map of field-name → selector pairs attached to a scraper target |
| **Scraper target** | A configured source site (name + URL + selector_map + schedule) |
| **SLO** | Service Level Objective — measurable reliability/performance target |
| **SPA** | Single-Page Application — JS-heavy site that requires a real browser |
| **Static site** | Server-rendered HTML where httpx + parser suffice (no browser needed) |
| **CronTrigger** | APScheduler trigger type using a cron expression for periodic firing |
| **Jobstore** | Persistent APScheduler backing store (we use SQLAlchemy jobstore on PG) |
| **Retry budget** | Maximum number of retry attempts before a job is routed to DLQ |
| **Backoff** | Delay inserted between retries (exponential backoff by default) |
| **External ID** | Source-supplied identifier used as the dedup key in `records.external_id` |
| **Payload** | The normalized, Pydantic-validated record body stored as JSONB |
| **External_id key** | Tuple `(target_id, external_id)` enforcing unique scraped rows |
| **Run** | A single execution of a scraper target with a `runs` table history record |
| **Healthcheck** | HTTP endpoint (`/healthz`) returning liveness/readiness for orchestration |
| **Admin endpoint** | FastAPI route used by the operator (status, DLQ inspection, manual trigger) |
| **Bootstrap** | One-shot initial schema/seed step run on first container start |
| **Recovery** | Process of inspecting DLQ entries and re-queueing after manual fix |
| **Trace** | Playwright trace log captured when a scrape fails (for forensics) |
| **Notifier** | Component that fans out alerts (Telegram, file log) on job events |
| **Snapshot** | Materialized CSV or Google-Sheets output reflecting the current record set |
| **Window** | Time-bounded slice of records (e.g., "last 24h") used in scheduled runs |
MDEOF
