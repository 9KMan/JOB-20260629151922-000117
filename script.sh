# After Phase 2 lands, this one-liner boots the entire stack:
docker compose up -d

# Manual scrape run (Operator CLI):
docker compose exec pipeline python -m pipeline.cli run --target <name>

# Healthcheck:
curl http://localhost:8000/healthz
