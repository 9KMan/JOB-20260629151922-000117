"""Settings load with sensible defaults."""
from __future__ import annotations

from bpa.config import Settings


def test_defaults() -> None:
    s = Settings()
    assert s.app_name == "bpa-pipeline"
    assert s.environment == "development"
    assert s.database_pool_size == 5
    assert s.playwright_headless is True
