python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium
cp .env.example .env
alembic upgrade head
uvicorn bpa.main:app --reload
