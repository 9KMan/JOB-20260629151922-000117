# Glossary

| Term | Definition |
|------|------------|
| **DLQ** | Dead-Letter Queue — table holding jobs that exhausted their retry budget |
| **ETL** | Extract, Transform, Load — the canonical pipeline pattern this project follows |
| **Idempotent fetch** | A scrape run whose repeated execution produces the same final state (no duplicates) |
| **Job** | A scheduled unit of work (one scrape window, one delivery task) |
| **Operator** | The human who monitors the pipeline and acts on Telegram alerts |
| **Poison message** | A record that fails validation repeatedly and is routed to DLQ |
| **Selector** | A Playwright/CSS/XPath locator pointing at an element on a target page |
| **Target site** | A configured source website that the pipeline scrapes |
| **Selector map** | The YAML/JSON dict mapping record fields to Playwright selectors for a target |
| **Run** | A single end-to-end execution of one target's scrape + persist + deliver cycle |
| **Backoff** | Exponential delay between retry attempts (e.g. 2s, 4s, 8s) |
| **Jobstore** | APScheduler persistence backend; we use SQLAlchemyJobStore on PostgreSQL |
| **CronTrigger** | APScheduler trigger type accepting standard cron expressions |
| **Service account** | Google Cloud IAM identity used to authenticate the Sheets API client |
| **Healthcheck** | `/healthz` endpoint probing liveness of API, DB, scheduler, and browser pool |
| **Trace** | Playwright trace recording captured on scraping failure for debugging |
| **Docker compose** | Multi-container orchestration file used for local + production-like boot |
| **Uvicorn** | ASGI server that runs the FastAPI app |
| **asyncpg** | High-performance async PostgreSQL driver used by SQLAlchemy |
| **httpx** | Async/sync HTTP client used for Telegram + Google Sheets API calls |
| **MVP** | Minimum Viable Product — scope of this project |
| **Webhook** | Inbound HTTP callback (out of scope for MVP) |
| **SLO** | Service Level Objective — uptime/latency target (TBD) |

## Usage Conventions

- **"Pipeline"** always refers to the entire ETL chain end-to-end, including scheduling.
- **"Scraper"** is reserved for the Playwright/httpx extraction step only.
- **"Job"** is distinct from **"Run"** — a job is the scheduled definition; a run is its instance.
- **"Record"** refers to a single normalized Pydantic model instance after parsing.
- **"Operator"** is never used as a generic "user" — it is the human on Telegram.
