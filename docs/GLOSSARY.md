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
| **Scrape window** | The bounded time range a single scrape run covers |
| **Source site** | A target website configured for scraping in `scraper_targets` |
| **Sticky selector** | A selector resilient to minor DOM shifts (data attributes > nth-child) |
| **Target** | Synonym for source site in this codebase |
| **Backoff** | Increasing delay between retry attempts (e.g. 1s, 4s, 16s) |
| **Jobstore** | Persistent storage for APScheduler jobs (SQLAlchemy jobstore) |
| **Notifier** | Component that dispatches alerts (Telegram, log file) |
| **Orchestrator** | The module that coordinates scraping, parsing, persistence, and delivery |
| **Pydantic schema** | The typed record model validated after parsing |
| **Trace** | Playwright trace artifact capturing browser state for post-mortem debugging |
| **Worker** | A coroutine that performs a single scraping invocation |
