# Planned layout
pipeline/
  scrapers/      # Playwright + httpx adapters
  parsers/       # Pydantic schemas and normalizers
  db/            # SQLAlchemy models, Alembic migrations
  delivery/      # CSV, Sheets, Telegram
  scheduler/     # APScheduler wiring
  api/           # FastAPI app
  cli.py         # python -m pipeline.cli
tests/
docker-compose.yml
Dockerfile
pyproject.toml
