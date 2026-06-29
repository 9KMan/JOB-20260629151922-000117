# BPA Pipeline

Business Process Automation — Web Scraping + Data Pipeline (MVP).

Automated ETL pipeline that scrapes configurable target sites with Playwright, normalizes records via Pydantic, persists them in PostgreSQL with idempotent upserts, and delivers results as CSV / Google Sheets / Telegram notifications.

## Stack

- Python 3.12
- FastAPI + Uvicorn
- Playwright (Chromium)
- SQLAlchemy 2 (async) + asyncpg + Alembic
- APScheduler
- Pydantic v2 + pydantic-settings
- structlog
- python-telegram-bot, gspread, httpx, tenacity

## Quick start (local)

