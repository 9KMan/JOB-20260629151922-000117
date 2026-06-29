cat > src/bpa/main.py << 'EOF'
"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from bpa.config import get_settings
from bpa.logging_setup import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log = get_logger(__name__)
    settings = get_settings()
    log.info("app.starting", env=settings.environment, name=settings.app_name)
    yield
    log.info("app.stopped")


app = FastAPI(
    title="BPA Pipeline",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
EOF
