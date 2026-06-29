# BPA Pipeline

Business Process Automation — Web Scraping + Data Pipeline (MVP).

Automates the collection, normalization, and delivery of business data scraped
from configured target sites, replacing manual copy-paste with a reproducible
ETL pipeline.

## Stack

- Python 3.12
- Playwright (Chromium) + httpx fallback
- FastAPI + Uvicorn
- PostgreSQL 15 + SQLAlchemy 2 (async) + Alembic
- APScheduler (in-process cron)
- Optional: Telegram Bot, Google Sheets
- structlog for JSON logs

## Quickstart (Docker)

