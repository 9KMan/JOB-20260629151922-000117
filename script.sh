# 1. Boot the stack (PostgreSQL + pipeline service)
docker compose up -d

# 2. Verify health
curl -fsS http://localhost:8000/health

# 3. Trigger a manual run for one target
docker compose exec pipeline python -m pipeline.cli run --target default
