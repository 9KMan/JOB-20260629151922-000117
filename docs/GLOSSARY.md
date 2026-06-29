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
| **Selector map** | JSON dictionary mapping logical field names (e.g. `name`, `phone`) to selectors per target site |
| **Scraper target** | A configured source site defined in `scraper_targets` with URL + selector map + cron schedule |
| **Scrape window** | The temporal scope of a single scheduled run (e.g. "today's listings") |
| **Retry budget** | Maximum number of attempts before a job is moved to the DLQ |
| **Exponential backoff** | Retry delay strategy: `delay = base * (2 ** attempt)` |
| **CronTrigger** | APScheduler trigger type that fires on a cron expression (default: `0 9 * * *`) |
| **Jobstore** | APScheduler persistence layer (SQLAlchemy jobstore on PostgreSQL) |
| **External ID** | Source-provided unique key per record; pairs with `target_id` to enforce idempotency |
| **Payload** | Normalized JSON record body stored in `records.payload` (Pydantic-validated) |
| **Run** | One execution instance of a job; tracked in `runs` table with started/finished status |
| **Delivery channel** | One of: CSV export, Google Sheets, Telegram notification |
| **Service token** | Google service-account credentials JSON, supplied via env var `GOOGLE_SERVICE_ACCOUNT_JSON` |
| **Bot token** | Telegram bot API token, supplied via env var `TELEGRAM_BOT_TOKEN` |
| **Chat ID** | Telegram chat identifier for alert routing, supplied via env var `TELEGRAM_CHAT_ID` |
| **Trace** | Playwright trace artifact captured on scrape failure for offline debugging |
| **Playwright fallback (httpx)** | Pure-server-rendered sites scraped via `httpx + selectolax` instead of a browser |
| **Backoff base** | Configurable initial delay (seconds) for exponential retry; default `2.0` |
| **Max retries** | Configurable retry budget cap; default `3` |
| **Healthcheck** | `/healthz` endpoint returning 200 OK when scheduler + DB are reachable |
| **Status endpoint** | `/status` endpoint returning last-run timestamps, success/fail counts, DLQ depth |
| **DLQ endpoint** | `/dlq` endpoint exposing poison messages for operator triage |
| **UTC schedule** | All cron expressions evaluate in UTC; default scrape time is `09:00 UTC` daily |
| **Single-instance deployment** | Constraint: one scheduler, one web worker, one DB — no horizontal scaling |
