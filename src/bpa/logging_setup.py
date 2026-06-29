"""Loguru JSON logging configuration."""
from __future__ import annotations

import json
import sys
from typing import Any

from loguru import logger

from bpa.config import get_settings


_configured = False


def _json_sink(message: Any) -> None:
    """Sink that emits structured JSON records to stdout.

    Loguru's record object exposes a `.record` dict with metadata. We pull out
    the fields we care about (timestamp, level, message, module, extra) and
    serialize them as a single line of JSON.
    """
    record = message.record
    payload = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    extra = record.get("extra") or {}
    if extra:
        payload["extra"] = extra
    if record["exception"] is not None:
        payload["exception"] = str(record["exception"])
    sys.stdout.write(json.dumps(payload, default=str) + "\n")
    sys.stdout.flush()


def configure_logging() -> None:
    """Configure the global loguru logger with a JSON sink.

    Safe to call multiple times; subsequent calls replace the handler.
    """
    global _configured
    settings = get_settings()
    logger.remove()
    logger.add(
        _json_sink,
        level=settings.log_level.upper(),
        enqueue=False,
        backtrace=False,
        diagnose=False,
    )
    _configured = True


def get_logger(name: str | None = None):
    """Return a bound logger. Falls back to the global logger."""
    if name:
        return logger.bind(module=name)
    return logger


def is_configured() -> bool:
    """Test helper — true after configure_logging() has been called."""
    return _configured