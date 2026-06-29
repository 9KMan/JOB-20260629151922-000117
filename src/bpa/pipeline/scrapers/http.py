"""Lightweight HTTP scraper using httpx + selectolax.

This is the fast path for server-rendered sites: no JS execution, just a
GET + CSS selector extraction. It can also be used as a smoke-test stub by
pointing at a local HTML fixture.
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


class HttpScraper(Scraper):
    mode = "http"

    def __init__(self, timeout: float = 20.0, max_retries: int = 0) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Any | None = None
        self._lock = asyncio.Lock()

    async def _ensure_client(self) -> None:
        async with self._lock:
            if self._client is not None:
                return
            try:
                import httpx  # type: ignore
            except ImportError as exc:  # pragma: no cover
                raise PermanentScraperError(
                    "httpx is not installed; install with `pip install httpx`"
                ) from exc
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": get_settings().scraper_default_user_agent},
                follow_redirects=True,
            )

    async def fetch(self, target: ScraperTarget) -> str:
        """GET the target URL and return the raw HTML body."""
        if not target.url:
            raise PermanentScraperError(f"target {target.name!r} has no url")
        await self._ensure_client()
        assert self._client is not None
        last_exc: Exception | None = None
        attempts = max(1, self.max_retries + 1)
        for attempt in range(attempts):
            try:
                response = await self._client.get(target.url)
            except Exception as exc:  # noqa: BLE001 — httpx raises many types
                last_exc = exc
                if attempt + 1 < attempts:
                    await asyncio.sleep(0.05 * (2 ** attempt))
                    continue
                raise TransientScraperError(
                    f"http fetch failed for {target.url}: {exc}"
                ) from exc
            status = response.status_code
            if status >= 500:
                last_exc = TransientScraperError(
                    f"http {status} from {target.url}"
                )
                if attempt + 1 < attempts:
                    await asyncio.sleep(0.05 * (2 ** attempt))
                    continue
                raise last_exc
            if status >= 400:
                raise PermanentScraperError(
                    f"http {status} (client error) from {target.url}"
                )
            return response.text
        # Should be unreachable, but be defensive
        raise TransientScraperError(
            f"http fetch exhausted retries for {target.url}: {last_exc}"
        )

    async def close(self) -> None:
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None


def html_to_records(html: str, target: ScraperTarget) -> list[dict[str, Any]]:
    """Parse HTML using selectolax and return a list of record dicts.

    This is a pure function (no DB, no network) so it can be unit-tested with
    inline HTML strings.
    """
    try:
        from selectolax.parser import HTMLParser  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise PermanentScraperError(
            "selectolax is not installed; install with `pip install selectolax`"
        ) from exc
    tree = HTMLParser(html)
    smap = target.selector_map
    rows = tree.css(smap.row)
    records: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        rec: dict[str, Any] = {}
        for field_name, selector in smap.field_selectors().items():
            node = row.css_first(selector)
            if node is None:
                rec[field_name] = None
            else:
                rec[field_name] = (node.text() or "").strip()
        # Always include an external_id so we can dedupe
        rec.setdefault("external_id", f"{target.name}-{idx}")
        records.append(rec)
    return records