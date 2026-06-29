"""Tenacity-backed retry decorator with exponential backoff."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from bpa.config import get_settings
from bpa.pipeline.scrapers.base import TransientScraperError

T = TypeVar("T")


def make_retry(
    *,
    max_attempts: int | None = None,
    initial_wait: float | None = None,
    max_wait: float | None = None,
    retry_on: tuple[type[BaseException], ...] = (TransientScraperError,),
) -> AsyncRetrying:
    """Build a configured tenacity AsyncRetrying object.

    Callers use this inside an `async for attempt in make_retry():` block.
    """
    settings = get_settings()
    return AsyncRetrying(
        stop=stop_after_attempt(max_attempts or settings.retry_max_attempts),
        wait=wait_exponential(
            multiplier=initial_wait or settings.retry_initial_wait_seconds,
            max=max_wait or settings.retry_max_wait_seconds,
        ),
        retry=retry_if_exception_type(retry_on),
        reraise=True,
    )


def retry_async(
    func: Callable[..., Any],
    *,
    max_attempts: int | None = None,
    initial_wait: float | None = None,
    max_wait: float | None = None,
    retry_on: tuple[type[BaseException], ...] = (TransientScraperError,),
) -> Callable[..., Any]:
    """Decorator that retries an async function on transient errors.

    Usage:
        @retry_async
        async def fetch(): ...
    """
    settings = get_settings()
    attempts = max_attempts or settings.retry_max_attempts
    init = initial_wait or settings.retry_initial_wait_seconds
    top = max_wait or settings.retry_max_wait_seconds

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        last_exc: BaseException | None = None
        for attempt in range(1, attempts + 1):
            try:
                return await func(*args, **kwargs)
            except retry_on as exc:
                last_exc = exc
                if attempt >= attempts:
                    raise
                # Exponential backoff: 1, 2, 4, ... seconds, capped at top
                delay = min(init * (2 ** (attempt - 1)), top)
                import asyncio

                await asyncio.sleep(delay)
        # Should never reach here, but be explicit
        if last_exc is not None:
            raise last_exc
        raise RetryError("retry_async exited without success")

    wrapper.__name__ = getattr(func, "__name__", "retry_wrapped")
    wrapper.__doc__ = func.__doc__
    return wrapper


__all__ = ["make_retry", "retry_async"]