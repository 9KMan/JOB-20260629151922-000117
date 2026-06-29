"""Playwright browser-based scraper.

This is the heavy-duty scraper for sites that render content via JavaScript.
It can be slow (multiple seconds per page) so callers should use it sparingly.
The browser is launched lazily on first use and reused across fetch() calls.
"""
from __future__ import annotations

import asyncio
from typing import Any

from bpa.config import get_settings
from bpa.pipeline.scrapers.base import (
    PermanentScraperError,
    Scraper,
    ScraperTarget,
    TransientScraperError,
)


class PlaywrightScraper(Scraper):
    mode = "playwright"

    def __init__(self, headless: bool = True, timeout_ms: int | None = None) -> None:
        self.headless = headless
        self.timeout_ms = timeout_ms or get_settings().scraper_default_timeout_ms
        self._playwright: Any | None = None
        self._browser: Any | None = None
        self._lock = asyncio.Lock()

    async def _ensure_browser(self) -> None:
        """Lazily launch playwright + chromium on first use."""
        async with self._lock:
            if self._browser is not None:
                return
            try:
                from playwright.async_api import async_playwright  # type: ignore
            except ImportError as exc:  # pragma: no cover - optional dep
                raise PermanentScraperError(
                    "playwright is not installed; install with `pip install playwright` "
                    "and run `playwright install chromium`"
                ) from exc
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=self.headless)

    async def fetch(self, target: ScraperTarget) -> str:
        """Navigate to the target URL and return the rendered HTML."""
        if not target.url:
            raise PermanentScraperError(f"target {target.name!r} has no url")
        await self._ensure_browser()
        assert self._browser is not None
        try:
            context = await self._browser.new_context(
                user_agent=get_settings().scraper_default_user_agent
            )
            page = await context.new_page()
            try:
                response = await page.goto(target.url, timeout=self.timeout_ms)
                if response is None:
                    raise TransientScraperError(
                        f"playwright got no response for {target.url}"
                    )
                status = response.status
                if status >= 500:
                    raise TransientScraperError(
                        f"playwright got HTTP {status} from {target.url}"
                    )
                if status >= 400:
                    raise PermanentScraperError(
                        f"playwright got HTTP {status} from {target.url}"
                    )
                # Wait for selector_map.row to be present, if configured
                row_selector = target.selector_map.row
                try:
                    await page.wait_for_selector(row_selector, timeout=self.timeout_ms)
                except Exception:
                    # Fall back to just grabbing whatever rendered
                    pass
                html = await page.content()
                return html
            finally:
                await context.close()
        except TransientScraperError:
            raise
        except PermanentScraperError:
            raise
        except Exception as exc:  # noqa: BLE001 — playwright raises many types
            # Treat generic errors as transient so the orchestrator can retry
            raise TransientScraperError(
                f"playwright fetch failed for {target.url}: {exc}"
            ) from exc

    async def close(self) -> None:
        """Tear down browser + playwright instance."""
        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None