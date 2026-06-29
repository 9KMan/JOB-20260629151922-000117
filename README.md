# BPA Pipeline

Business Process Automation — Web Scraping + Data Pipeline (MVP).

Scrapes business data from configurable target sites, normalizes records with Pydantic, stores them in PostgreSQL with idempotent upserts, and delivers results as CSV (and optionally Google Sheets + Telegram notifications).

## Stack

- Python 3.12 + Playwright + FastAPI
- PostgreSQL 15 + SQLAlchemy 2 (async)
- APScheduler (in-process cron)
- python-telegram-bot + gspread
- Docker / docker-compose

## Quick Start

