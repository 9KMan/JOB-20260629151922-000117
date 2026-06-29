docs/PROJECT_OVERVIEW.md
# Project Overview

**Project ID:** JOB-20260629151922-000117
**Status:** MVP (Minimum Viable Product)
**Last Updated:** 2026-06-29

---

## 1. Purpose

Replace manual copy-paste workflows across 2–3 target websites with an automated
ETL pipeline that scrapes, cleans, stores, and delivers business data on a
recurring schedule. The MVP delivers a single-instance, Dockerized service that
an operator can monitor via Telegram and extend without rewriting the core.

## 2. Problem Statement

| Pain Point | Current State | Desired State |
|------------|---------------|---------------|
| Manual data entry | Operator copies data from 2–3 sites into spreadsheets | Automated fetch on cron schedule |
| Inconsistent records | Human error, formatting drift | Pydantic-validated structured records |
| No history | Spreadsheets overwritten, no audit trail | PostgreSQL-backed append-only history |
| Slow delivery | Operator manually compiles CSV | Auto-delivery via CSV, Google Sheets, Telegram |
| Brittle retries | Manual re-runs after failure | Idempotent fetches + retry queue + DLQ |

## 3. Scope

### 3.1 In Scope (MVP)

- Web scraping via Playwright (headless Chromium)
- HTML → structured record transformation via Pydantic v2
- PostgreSQL persistence via SQLAlchemy 2.0 (async) + asyncpg
- Scheduling via APScheduler with CronTrigger
- Delivery channels: CSV export, Google Sheets API, Telegram Bot API
- Retry queue with exponential backoff
- Dead-letter queue (DLQ) for poison messages
- FastAPI admin/status endpoint
- Docker-based deployment (single instance)
- Async HTTP client (httpx) for API integrations

### 3.2 Out of Scope (MVP)

- Distributed scheduling (single-instance only — APScheduler trade-off accepted)
- Horizontal scaling / Kubernetes orchestration
- Multi-tenant isolation
- Real-time streaming (batch/cron only)
- Mobile applications
- Custom dashboard UI (Telegram + CSV are the operator surfaces)

### 3.3 Out of Scope (Deferred — Post-MVP)

- Redis-backed job queue migration
- Machine-learning-based data cleansing
- Source-site anti-bot countermeasures beyond Playwright defaults
- SSO / RBAC for the admin endpoint
- Webhook ingress

## 4. Success Criteria

| # | Criterion | Measurement |
|---|-----------|-------------|
| SC-1 | Pipeline runs end-to-end without manual intervention | Successful cron execution → Telegram summary delivered |
| SC-2 | Scraped records persist to PostgreSQL with idempotent dedup | Re-running the same scrape window produces zero duplicate rows |
| SC-3 | Failed jobs retry with backoff then land in DLQ | A simulated site failure appears in DLQ table within configured retry budget |
| SC-4 | Operator can verify pipeline health via Telegram | Status command returns last-run timestamp, success/fail counts, DLQ depth |
| SC-5 | Service deploys via single `docker compose up` | Containers start; healthcheck passes; scheduler ticks within 60s |

## 5. Stakeholders & Roles

| Role | Responsibility |
|------|----------------|
| Operator | Monitors Telegram alerts, reviews DLQ, adjusts cron config |
| Developer | Extends scrapers for new source sites, tunes selectors |
| End Consumer | Receives CSV / Google Sheets / Telegram digest |

## 6. High-Level Architecture

