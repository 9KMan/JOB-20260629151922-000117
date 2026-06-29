# 1. Clone & configure
cp .env.example .env
# edit .env with DB credentials, Telegram bot token, Google Sheets service-account JSON path

# 2. Boot the stack
docker compose up -d

# 3. Verify
curl http://localhost:8000/healthz
