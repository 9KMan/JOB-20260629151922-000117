# Glossary

| Term | Definition |
|------|------------|
| **DLQ** | Dead-Letter Queue — table holding jobs that exhausted their retry budget |
| **ETL** | Extract, Transform, Load — the canonical pipeline pattern this project follows |
| **Idempotent fetch** | A scrape run whose repeated execution produces the same final state (no duplicates) |
| **Job** | A scheduled unit of work (one scrape window, one delivery task) |
| **Operator** | The human who monitors the pipeline and acts on Telegram alerts |
| **Poison message** | A record that fails validation repeatedly and is routed to DLQ |
| **Selector** | A Playwright/CSS/XPath locator pointing at an HTML element to extract |
| **Scrape window** | The bounded time range or page-set a single scrape job covers |
| **Target** | A configured source site (name, URL, selector map, schedule) |
| **Trace** | A Playwright trace artifact capturing navigation + DOM for debugging |
| **Backoff** | Incremental delay between retry attempts, typically exponential |
| **Upsert** | INSERT ... ON CONFLICT DO UPDATE — provides idempotent persistence |
| **Jobstore** | APScheduler's persistence backend (SQLAlchemy jobstore on PG in this project) |
| **External ID** | A source-defined stable identifier used as the dedup key |
| **Payload** | The normalized, Pydantic-validated JSON record stored in PostgreSQL |
| **CronTrigger** | APScheduler trigger type that fires on cron-style schedules |
| **Service account** | A non-human Google identity used to authorize the Sheets API client |
| **Healthcheck** | A lightweight HTTP probe (e.g., `/healthz`) used by Docker and orchestrators |
| **Run history** | The append-only `runs` table recording each pipeline execution |
| **CSV export** | File-based delivery artifact, one row per normalized record |
