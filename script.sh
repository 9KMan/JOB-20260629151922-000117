# 1. Clone and configure
cp .env.example .env
# edit .env with DATABASE_URL, TELEGRAM_BOT_TOKEN, etc.

# 2. Launch
docker compose up -d

# 3. Verify
curl http://localhost:8000/healthz
