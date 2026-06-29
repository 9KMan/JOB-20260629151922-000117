"""Telegram notifier.

Optional integration — if TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID are unset
or python-telegram-bot isn't installed, the send_message functions return a
"skipped" status instead of raising.
"""
from __future__ import annotations

import asyncio
from typing import Any

from bpa.config import get_settings
from bpa.logging_setup import get_logger

log = get_logger(__name__)


def _credentials_available() -> tuple[bool, str | None]:
    settings = get_settings()
    if not settings.telegram_bot_token:
        return False, "TELEGRAM_BOT_TOKEN not set"
    if not settings.telegram_chat_id:
        return False, "TELEGRAM_CHAT_ID not set"
    return True, None


async def send_message(text: str) -> tuple[bool, str]:
    """Send a message to the configured Telegram chat. Returns (ok, message)."""
    ok, err = _credentials_available()
    if not ok:
        log.warning("telegram.skipped", reason=err)
        return False, f"skipped: {err}"
    try:
        from telegram import Bot  # type: ignore
    except ImportError:
        msg = "python-telegram-bot not installed"
        log.warning("telegram.skipped", reason=msg)
        return False, msg
    settings = get_settings()
    try:
        bot = Bot(token=settings.telegram_bot_token)
        await bot.send_message(chat_id=settings.telegram_chat_id, text=text)
        log.info("telegram.sent", length=len(text))
        return True, "sent"
    except Exception as exc:  # noqa: BLE001
        msg = f"telegram send failed: {exc}"
        log.error("telegram.error", error=str(exc))
        return False, msg


def send_message_sync(text: str) -> tuple[bool, str]:
    """Sync wrapper around send_message for non-async callers."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop is None:
        return asyncio.run(send_message(text))
    # If we're already inside an event loop, run the coroutine on it
    return loop.run_until_complete(send_message(text))


async def send_summary(
    *,
    target_name: str,
    new_count: int,
    updated_count: int,
    error_count: int = 0,
) -> tuple[bool, str]:
    """Send a short run-summary message to Telegram."""
    text = (
        f"✅ {target_name}\n"
        f"  new: {new_count}\n"
        f"  updated: {updated_count}\n"
        f"  errors: {error_count}"
    )
    return await send_message(text)


__all__ = ["send_message", "send_message_sync", "send_summary"]