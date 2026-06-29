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
| **Selector** | A Playwright/CSS/XPath locator pointing at an element on the target page |
| **Selector map** | JSON document mapping logical field names to selectors for a given target |
| **Scraper target** | A configured source site (URL + selector map + schedule) stored in `scraper_targets` |
| **Run** | A single execution of a scrape job, recorded in the `runs` table |
| **External ID** | Stable identifier from the source site used as the dedup key alongside `target_id` |
| **Payload** | The normalized JSON-serializable record produced from raw HTML |
| **Delivery channel** | One of: CSV export, Google Sheets, Telegram summary |
| **Backoff** | Increasing delay between retries (e.g., 2s, 4s, 8s) |
| **Retry budget** | Maximum number of retry attempts before a job is moved to DLQ |
| **Cron expression** | Schedule string (e.g., `0 9 * * *`) consumed by APScheduler CronTrigger |
| **Healthcheck** | A FastAPI endpoint returning service liveness/readiness |
| **Jobstore** | APScheduler persistence backend (SQLAlchemy jobstore in this project) |
| **Trace** | Playwright artifact (zip) capturing network + DOM for failed scrMDEOF
