# BPA Pipeline

**Business Process Automation — Web Scraping + Data Pipeline (MVP).**

Automates the scraping, normalization, and delivery of business data from configurable
target sites. Built on Python 3.12, Playwright, FastAPI, PostgreSQL, APScheduler, and Docker.

## Stack

- **Python 3.12** runtime
- **Playwright** (Chromium, headless) for modern / JS-rendered sites
- **httpx** + **selectolax** for fast static-page scraping
- **Pydantic v2** for typed records
- **FastAPI** + **Uvicorn** for the admin API and `/health` probe
- **PostgreSQL 15** + **SQLAlchemy 2 (async)** + **Alembic** for storage
- **APScheduler** for cron-style execution
- **python-telegram-bot** for completion/failure notifications
- **gspread** for Google Sheets export
- **loguru / structlog** for structured JSON logs
- **Docker** + **docker compose** for one-command bootstrap

## Quick start

