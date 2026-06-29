# 1. Clone and enter the repo
git clone <repo-url> && cd <repo>

# 2. Copy and edit environment variables
cp .env.example .env
$EDITOR .env   # set DATABASE_URL, TELEGRAM_BOT_TOKEN, GOOGLE_CREDS_PATH, etc.

# 3. Boot the stack (PostgreSQL + pipeline + FastAPI)
docker compose up -d

# 4. Verify health
curl -s http://localhost:8000/healthz | jq .
