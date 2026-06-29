# 1. Configure environment
cp .env.example .env        # then fill in DATABASE_URL, TELEGRAM_BOT_TOKEN, etc.

# 2. Boot the stack
docker compose up -d

# 3. Verify
curl http://localhost:8000/healthz
