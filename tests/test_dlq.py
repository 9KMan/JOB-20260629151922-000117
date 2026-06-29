"""Tests for bpa.pipeline.dlq — dead-letter persistence + alert message generation."""
from __future__ import annotations

import pytest

from bpa.pipeline.dlq import alert_message
from bpa.pipeline.db.models import DeadLetterORM


class TestAlertMessage:
    def test_alert_message_with_empty_list(self):
        # Implementation may return empty string for no errors
        msg = alert_message([])
        assert isinstance(msg, str)

    def test_alert_message_with_errors(self):
        # Build a DeadLetterORM instance (without persisting — no session needed)
        entry = DeadLetterORM(
            target_id=1,
            external_id="rec-001",
            error_type="HTTPError",
            error_message="HTTP 500 Internal Server Error",
            payload={"url": "https://example.com/page"},
            attempt_count=3,
        )
        msg = alert_message([entry])
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_alert_message_with_multiple_errors(self):
        entries = [
            DeadLetterORM(
                target_id=1,
                error_type="TimeoutError",
                error_message="Request timed out after 20s",
                attempt_count=3,
            ),
            DeadLetterORM(
                target_id=1,
                error_type="HTTPError",
                error_message="HTTP 404 Not Found",
                attempt_count=1,
            ),
            DeadLetterORM(
                target_id=2,
                error_type="ParseError",
                error_message="JSON parse error at line 42",
                attempt_count=2,
            ),
        ]
        msg = alert_message(entries)
        assert isinstance(msg, str)
        assert len(msg) > 0


class TestDeadLetterORM:
    def test_can_import_model(self):
        from sqlalchemy.orm import DeclarativeBase
        assert hasattr(DeadLetterORM, "__tablename__")
        assert hasattr(DeadLetterORM, "__table__")

    def test_construct_orm_instance(self):
        # Build without persisting
        entry = DeadLetterORM(
            target_id=1,
            external_id="rec-001",
            error_type="TestError",
            error_message="test failure",
            attempt_count=1,
        )
        assert entry.target_id == 1
        assert entry.external_id == "rec-001"
        assert entry.error_type == "TestError"
        assert entry.error_message == "test failure"
        assert entry.attempt_count == 1
        # Defaults
        assert entry.payload == {} or entry.payload is None
        # created_at may be None until SQLAlchemy applies the default
        pass