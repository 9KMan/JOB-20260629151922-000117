"""Tests for bpa.pipeline.retry — tenacity-backed async retry decorator."""
from __future__ import annotations

import asyncio
import pytest

from bpa.pipeline.retry import retry_async, make_retry
from bpa.pipeline.scrapers.base import TransientScraperError, PermanentScraperError


class TestMakeRetry:
    def test_make_retry_returns_tenacity_object(self):
        retrier = make_retry(max_attempts=3, initial_wait=0.01, max_wait=0.1)
        assert retrier is not None
        assert hasattr(retrier, "stop")
        assert hasattr(retrier, "wait")


def _wrap(fn, **kwargs):
    """Helper: retry_async takes a function as first arg.

    retry_async(func, *, max_attempts=None, ...) is a function-decorator that
    can also be called inline. This helper makes the call site explicit.
    """
    return retry_async(fn, **kwargs)


class TestRetryAsyncSuccess:
    @pytest.mark.asyncio
    async def test_returns_value_on_first_try(self):
        async def succeed():
            return "ok"

        wrapped = _wrap(succeed, max_attempts=3, initial_wait=0.01, max_wait=0.1)
        result = await wrapped()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_retries_then_succeeds(self):
        attempts = []

        async def flaky():
            attempts.append(1)
            if len(attempts) < 3:
                raise TransientScraperError("transient")
            return "ok"

        wrapped = _wrap(flaky, max_attempts=3, initial_wait=0.01, max_wait=0.1)
        result = await wrapped()
        assert result == "ok"
        assert len(attempts) == 3


class TestRetryAsyncFailure:
    @pytest.mark.asyncio
    async def test_gives_up_after_max_attempts(self):
        attempts = []

        async def always_fails():
            attempts.append(1)
            raise TransientScraperError("always fails")

        wrapped = _wrap(always_fails, max_attempts=3, initial_wait=0.01, max_wait=0.1)
        with pytest.raises(TransientScraperError):
            await wrapped()
        assert len(attempts) == 3

    @pytest.mark.asyncio
    async def test_permanent_error_not_retried(self):
        attempts = []

        async def permanent_fail():
            attempts.append(1)
            raise PermanentScraperError("permanent")

        wrapped = _wrap(permanent_fail, max_attempts=3, initial_wait=0.01, max_wait=0.1,
                        retry_on=(TransientScraperError,))
        with pytest.raises(PermanentScraperError):
            await wrapped()
        # Permanent errors not in retry_on → only 1 attempt
        assert len(attempts) == 1

    @pytest.mark.asyncio
    async def test_unrelated_exception_not_retried(self):
        attempts = []

        async def value_error_fn():
            attempts.append(1)
            raise ValueError("not transient")

        wrapped = _wrap(value_error_fn, max_attempts=3, initial_wait=0.01, max_wait=0.1)
        with pytest.raises(ValueError):
            await wrapped()
        assert len(attempts) == 1