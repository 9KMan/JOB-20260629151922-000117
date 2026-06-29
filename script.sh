# Clone the repository
git clone <repo-url> business-pipeline
cd business-pipeline

# Bring up the stack
docker compose up -d

# Verify health
curl -fsS http://localhost:8000/health

# Trigger a manual run
docker compose exec app python -m pipeline.cli --target example-com
