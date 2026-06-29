"""Pytest configuration: ensure src/ is on sys.path and DB URL is set BEFORE app imports."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Set DATABASE_URL BEFORE any bpa.* import (Bug 184: SQLite + FastAPI TestClient needs
# check_same_thread=False; pydantic-settings reads env at import time).
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")

# Add src/ to sys.path so `import bpa.*` works.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Async test loop config
import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"