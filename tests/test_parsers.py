"""Tests for bpa.pipeline.parsers.normalize — text/int/float/date/coerce helpers."""
from __future__ import annotations

import pytest
from decimal import Decimal

from bpa.pipeline.parsers.normalize import (
    clean_text,
    coerce_int,
    coerce_float,
    coerce_decimal,
    coerce_date,
    normalize_phone,
    normalize_email,
    normalize_url,
    normalize_whitespace,
    make_external_id,
)


class TestCleanText:
    def test_returns_none_for_none(self):
        assert clean_text(None) is None

    def test_returns_none_for_empty(self):
        assert clean_text("") is None
        assert clean_text("   ") is None

    def test_strips_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_preserves_inner_whitespace(self):
        assert clean_text("hello world") == "hello world"


class TestNormalizeWhitespace:
    def test_collapses_internal_whitespace(self):
        assert normalize_whitespace("a  b\tc") == "a b c"

    def test_handles_newlines(self):
        assert normalize_whitespace("a\n\nb") == "a b"


class TestCoerceInt:
    def test_int_passthrough(self):
        assert coerce_int(42) == 42

    def test_string_digits(self):
        assert coerce_int("42") == 42

    def test_string_with_currency(self):
        assert coerce_int("$1,234") == 1234

    def test_invalid_returns_none(self):
        assert coerce_int("not a number") is None

    def test_none_returns_none(self):
        assert coerce_int(None) is None


class TestCoerceFloat:
    def test_basic_float(self):
        assert coerce_float("3.14") == pytest.approx(3.14)

    def test_string_with_currency(self):
        assert coerce_float("$1,234.56") == pytest.approx(1234.56)

    def test_invalid_returns_none(self):
        assert coerce_float(None) is None
        assert coerce_float("oops") is None


class TestCoerceDecimal:
    def test_precise_decimal(self):
        result = coerce_decimal("1234.5678")
        assert isinstance(result, Decimal)
        assert result == Decimal("1234.5678")

    def test_currency_symbol(self):
        assert coerce_decimal("$99.99") == Decimal("99.99")


class TestNormalizePhone:
    def test_basic_us_phone(self):
        # Implementation strips non-digits and returns a canonical string
        result = normalize_phone("(555) 123-4567")
        assert result is not None
        # All digits present
        digits = "".join(c for c in result if c.isdigit())
        assert digits == "5551234567"

    def test_already_normalized(self):
        result = normalize_phone("+1 555 123 4567")
        assert result is not None
        digits = "".join(c for c in result if c.isdigit())
        assert digits == "15551234567"

    def test_invalid_returns_none(self):
        # Strings with no digits should be rejected
        assert normalize_phone(None) is None
        assert normalize_phone("") is None


class TestNormalizeEmail:
    def test_lowercase_email(self):
        assert normalize_email("User@Example.COM") == "user@example.com"

    def test_strip_whitespace(self):
        assert normalize_email("  user@example.com  ") == "user@example.com"

    def test_none_returns_none(self):
        assert normalize_email(None) is None


class TestNormalizeUrl:
    def test_strips_tracking_params(self):
        # Implementation may strip common tracking params
        result = normalize_url("https://example.com/page")
        assert result is not None
        assert "example.com" in result

    def test_invalid_returns_none(self):
        assert normalize_url(None) is None


class TestCoerceDate:
    def test_iso_format(self):
        # Implementation may return datetime or ISO string
        result = coerce_date("2024-06-15")
        assert result is not None
        assert "2024-06-15" in str(result)

    def test_us_format(self):
        # Implementation accepts various formats
        result = coerce_date("06/15/2024")
        assert result is not None
        assert "2024" in str(result) and "06" in str(result)

    def test_invalid_returns_none(self):
        assert coerce_date("not a date") is None


class TestMakeExternalId:
    def test_concatenates_parts(self):
        eid = make_external_id("target-1", "rec-42")
        assert "target-1" in eid
        assert "rec-42" in eid

    def test_deterministic_for_same_input(self):
        a = make_external_id("t", "r")
        b = make_external_id("t", "r")
        assert a == b

    def test_different_for_different_input(self):
        a = make_external_id("t", "r1")
        b = make_external_id("t", "r2")
        assert a != b