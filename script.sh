# 1. Install dependencies
pip install -r requirements-dev.txt

# 2. Configure environment
cp .env.example .env  # then edit values
export DATABASE_URL=postgresql+asyncpg://bpa:bpa@localhost:5432/bpa

# 3. Run database migrations
alembic upgrade head

# 4. Start the API + scheduler
uvicorn bpa.main:app --reload
