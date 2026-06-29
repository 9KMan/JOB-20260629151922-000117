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
| **Source site** | An upstream website whose data we extract |
| **Target** | A registered source site, with schedule and selector map, stored in `scraper_targets` |
| **Run** | A single execution instance of a job, recorded in the `runs` table |
| **Cron trigger** | APScheduler primitive that fires jobs on calendar-based schedules |
| **Backoff** | Increasing delay between retry attempts (e.g. 1s → 2s → 4s) |
| **Record** | A normalized, Pydantic-validated row ready for persistence or delivery |
| **Payload** | The JSON-serialized form of a `Record` as stored in PostgreSQL |
| **External ID** | Source-provided unique identifier used as the dedup key |
| **Delivery channel** | One of: CSV file, Google Sheet, Telegram message |
| **Healthcheck** | `GET /healthz` endpoint confirming process liveness + DB reachability |
| **Jobstore** | APScheduler persistence layer (here: SQLAlchemy-backed on same PG) |
| **Trace** | Playwright network + DOM trace captured on selector failure for debugging |
