# BPA Pipeline

Business Process Automation — Web Scraping + Data Pipeline (MVP).

Automated ETL pipeline that scrapes business data from configured target sites,
normalizes records with Pydantic, persists them in PostgreSQL with idempotent
upserts, and delivers results via CSV / Google Sheets / Telegram.

## Stack

- Python 3.12 + Playwright + FastAPI + PostgreSQL 15
- SQLAlchemy 2 (async) + asyncpg + Alembic
- APScheduler, python-telegram-bot, gspread
- Structured logging via structlog

## Quickstart

