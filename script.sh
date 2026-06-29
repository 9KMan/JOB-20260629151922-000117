cp .env.example .env       # fill in DATABASE_URL, TELEGRAM_BOT_TOKEN, etc.
docker compose up -d       # starts PostgreSQL + the pipeline service
curl http://localhost:8000/healthz
