# Clone
git clone <repo-url>
cd <repo>

# Configure environment
cp .env.example .env
# edit .env with DATABASE_URL, TELEGRAM_BOT_TOKEN, GOOGLE_CREDENTIALS_JSON_PATH

# Boot the stack
docker compose up -d

# Verify
curl http://localhost:8000/healthz
