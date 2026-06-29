"""Normalization helpers — coerce raw strings into typed values.

These functions are deliberately pure (no IO) so they're trivially unit-
testable. Every helper accepts `None` and returns `None` rather than
raising, so callers can validate the whole batch before hitting the DB.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any


_WHITESPACE_RE = re.compile(r"\s+")
_CURRENCY_RE = re.compile(r"[^0-9.\-]")
_PHONE_RE = re.compile(r"[^\d+\-]")
_TRAILING_DASH_RE = re.compile(r"-+$")


def clean_text(value: Any) -> str | None:
    """Collapse whitespace and strip. Returns None if input is None/empty."""
    if value is None:
        return None
    s = str(value)
    s = _WHITESPACE_RE.sub(" ", s).strip()
    return s or None


def normalize_whitespace(value: Any) -> str | None:
    """Alias kept for backwards compatibility."""
    return clean_text(value)


def coerce_int(value: Any) -> int | None:
    """Parse an integer from a string. Strips currency symbols / commas."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    s = _CURRENCY_RE.sub("", str(value)).strip()
    s = _TRAILING_DASH_RE.sub("", s)
    if not s or s in {"-", "."}:
        return None
    try:
        return int(s)
    except ValueError:
        try:
            return int(float(s))
        except ValueError:
            return None


def coerce_float(value: Any) -> float | None:
    """Parse a float from a string. Returns None on failure."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    s = _CURRENCY_RE.sub("", str(value)).strip()
    if not s or s in {"-", "."}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def coerce_decimal(value: Any) -> Decimal | None:
    """Parse a Decimal — useful for prices/money where float precision matters."""
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    s = _CURRENCY_RE.sub("", str(value)).strip()
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def normalize_phone(value: Any) -> str | None:
    """Strip a phone number down to digits, +, and -."""
    if value is None or value == "":
        return None
    s = _PHONE_RE.sub("", str(value))
    s = _TRAILING_DASH_RE.sub("", s).strip()
    return s or None


def normalize_email(value: Any) -> str | None:
    """Lowercase + strip whitespace."""
    if value is None:
        return None
    s = str(value).strip().lower()
    return s or None


def normalize_url(value: Any) -> str | None:
    """Strip whitespace; return None if empty or missing scheme."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if "://" not in s:
        return None
    return s


def coerce_date(
    value: Any,
    *,
    formats: tuple[str, ...] = (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
    ),
) -> datetime | None:
    """Parse a date string using a list of common formats.

    Returns a timezone-aware UTC datetime on success.
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    s = str(value).strip()
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def make_external_id(*parts: Any) -> str:
    """Build a deterministic dedup key from one or more fields."""
    cleaned = [clean_text(p) or "" for p in parts]
    return "|".join(cleaned)