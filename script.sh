python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium
uvicorn bpa.main:app --reload --app-dir src
