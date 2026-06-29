# BPA Pipeline

Business Process Automation — Web Scraping + Data Pipeline (MVP).

## Overview

Automated ETL pipeline that:
1. Scrapes business data from configurable target sites (Playwright)
2. Cleans raw HTML into Pydantic-validated records
3. Stores records in PostgreSQL with idempotent upserts
4. Exports to CSV, Google Sheets, and Telegram summaries
5. Runs on a cron schedule with retry/DLQ safety nets

## Stack

- **Python 3.12** — runtime
- **Playwright** — modern Chromium-based scraper
- **FastAPI** — admin/health endpoints
- **PostgreSQL 15** — persistent record store
- **SQLAlchemy 2.0 (async)** — ORM + migrations via Alembic
- **APScheduler** — in-process cron scheduling
- **structlog** — structured JSON logging

## Quick Start

### Local (without Docker)

