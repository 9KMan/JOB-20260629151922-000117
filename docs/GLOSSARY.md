# Glossary

Shared vocabulary used across all project phases. Terms here are referenced
unambiguously in code, configuration, and operator-facing documentation.

| Term | Definition |
|------|------------|
| **DLQ** | Dead-Letter Queue — table holding jobs that exhausted their retry budget |
| **ETL** | Extract, Transform, Load — the canonical pipeline pattern this project follows |
| **Idempotent fetch** | A scrape run whose repeated execution produces the same final state (no duplicates) |
| **Job** | A scheduled unit of work (one scrape window, one delivery task) |
| **Operator** | The human who monitors the pipeline and acts on Telegram alerts |
| **Poison message** | A record that fails validation repeatedly and is routed to DLQ |
| **Selector** | A Playwright/CSS/XPath locator pointing at an element on the target site |
| **Selector map** | JSON object mapping logical field names to selector strings for one target |
| **Target** | A single configured source site/feed that the pipeline scrapes |
| **Run** | One execution of the pipeline for a specific target and time window |
| **Window** | The time-bounded set of records a scrape is expected to produce |
| **Backoff** | Increasing delay between retries (e.g. exponential: 1s, 2s, 4s, ...) |
| **Retry budget** | Maximum number of retry attempts before a job is dead-lettered |
| **Jobstore** | Persistent backing store used by APScheduler to survive process restarts |
| **Trigger** | APScheduler object defining when a job fires (Cron, Interval, Date) |
| **Cron expression** | Standard 5- or 6-field schedule string (e.g. `0 9 * * *` = daily 09:00 UTC) |
| **Asyncpg** | PostgreSQL async driver used by SQLAlchemy in this project |
| **Service account** | Google Cloud IAM identity used to authenticate the Sheets API client |
| **Bot token** | Telegram API credential identifying a specific bot installation |
| **Chat ID** | Telegram numeric identifier for a user, group, or channel that receives alerts |
| **Healthcheck** | Liveness probe exposed at `GET /health` returning service status |
| **Trace** | Playwright capture of network + DOM events used to debug scrape failures |
| **Worker** | Async coroutine that performs one phase of the ETL pipeline |
| **Orchestrator** | Component that wires scrapers, parsers, storage, and delivery together |
| **Upsert** | INSERT ... ON CONFLICT DO UPDATE — the dedup mechanism for records |
| **External ID** | Source-provided unique identifier used as the dedup key per (target, record) |
| **Payload** | Normalized Pydantic record body, serialized to JSONB for storage |
| **Source URL** | Canonical link back to the original scraped record, stored for verification |
| **MVP** | Minimum Viable Product — first usable scope that delivers end-to-end value |
| **Single-instance** | Deployment topology where one process hosts scheduler + API + scrapers |
| **Operator surface** | The set of UI/output channels an operator uses (Telegram bot, CSV export) |
