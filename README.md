# BPA Pipeline

Business Process Automation — Web Scraping + Data Pipeline (MVP).

A Playwright + FastAPI + PostgreSQL stack that scrapes configurable target sites, normalizes records with Pydantic, persists them with idempotent upserts, and delivers results as CSV exports, Google Sheets updates, and Telegram summaries.

## Stack

- **Python 3.12** (uv / hatchling)
- **Playwright** (Chromium) for JS-rendered sites, **httpx** + **selectolax** for static ones
- **FastAPI** + **Uvicorn** for the admin API (`/health`, CSV download)
- **PostgreSQL 15** via **SQLAlchemy 2 (async)** + **asyncpg**, schema managed by **Alembic**
- **APScheduler** for the daily 09:00 UTC cron
- **python-telegram-bot v21** for notifications
- **gspread** + service account for Google Sheets export
- **structlog** for structured JSON logs

## Quick start

