"""Abstract scraper interface and a tiny dataclass describing a target site."""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SelectorMap:
    """Maps semantic field names to CSS selectors.

    Conventions:
        row: selector that matches each individual record container
        fields: dict of {field_name: css_selector} extracted from each row
    """

    row: str = ".row"
    fields: dict[str, str] = field(default_factory=dict)

    def field_selectors(self) -> dict[str, str]:
        return dict(self.fields)


@dataclass
class ScraperTarget:
    """In-memory description of a target website.

    Mirrors the scraper_targets DB table but is also usable directly from
    a YAML config without a DB round-trip.
    """

    id: int | None
    name: str
    url: str
    mode: str = "http"  # "http" or "playwright"
    selector_map: SelectorMap = field(default_factory=SelectorMap)
    schedule: str = "0 9 * * *"
    enabled: bool = True
    extra: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.extra.get(key, default)


class Scraper(abc.ABC):
    """Abstract base for all scrapers.

    A scraper receives a target and returns raw HTML (or a list of already-
    extracted record dicts). Concrete implementations decide whether to use
    a real browser (Playwright) or just HTTP + CSS selectors.
    """

    mode: str = "abstract"

    @abc.abstractmethod
    async def fetch(self, target: ScraperTarget) -> str:
        """Return the raw HTML for the target URL."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Release any resources (browser, HTTP client)."""


class ScraperError(RuntimeError):
    """Raised when a scraper cannot complete its task.

    Transient errors (network timeouts, 5xx) should be retried by the
    orchestrator using the tenacity decorator. Permanent errors (bad URL,
    malformed config) go straight to the DLQ.
    """


class TransientScraperError(ScraperError):
    """Marker for errors worth retrying."""


class PermanentScraperError(ScraperError):
    """Marker for errors that should NOT be retried."""