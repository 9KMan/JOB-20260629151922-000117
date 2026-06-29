# Glossary

| Term | Definition |
|------|------------|
| **DLQ** | Dead-Letter Queue — table holding jobs that exhausted their retry budget |
| **ETL** | Extract, Transform, Load — the canonical pipeline pattern this project follows |
| **Idempotent fetch** | A scrape run whose repeated execution produces the same final state (no duplicates) |
| **Job** | A scheduled unit of work (one scrape window, one delivery task) |
| **Operator** | The human who monitors the pipeline and acts on Telegram alerts |
| **Poison message** | A record that fails validation repeatedly and is routed to DLQ |
| **Selector** | A Playwright/CSS/XPath locator pointing at an element on the target page |
| **Target site** | A configured source website (one row in `scraper_targets`) |
| **Window** | The time span of records a single scrape run is expected to capture |
| **Backoff** | Increasing delay between retry attempts (exponential schedule) |
| **Upsert** | INSERT … ON CONFLICT DO UPDATE; used to enforce idempotency on `(target_id, external_id)` |
| **Jobstore** | APScheduler persistence backend — here, a SQLAlchemy jobstore bound to PostgreSQL |
| **CronTrigger** | APScheduler trigger type driven by cron expressions |
| **Service Account** | Google Cloud IAM identity used by gspread to authenticate against Sheets API |
| **Bot Token** | Opaque secret issued by `@BotFather` authorizing calls to the Telegram Bot API |
| **Adapter** | Pluggable class that turns a raw page into normalized records (Playwright or httpx flavors) |
| **Record** | A single normalized business entry (Pydantic model) ready for storage |
| **Run** | One execution of a Job, recorded in the `runs` table for audit |
| **Healthcheck** | Liveness probe endpoint (`/healthz`) used by Docker / orchestrator |
| **Stack trace** | Captured exception text attached to a DLQ row for post-mortem |
| **Trace** | Playwright trace file written when a scrape fails for debugging |
