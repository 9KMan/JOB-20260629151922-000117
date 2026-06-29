docker compose up -d
docker compose exec api alembic upgrade head
