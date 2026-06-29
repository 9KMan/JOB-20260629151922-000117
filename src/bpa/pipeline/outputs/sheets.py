"""Google Sheets export via gspread.

The gspread import is optional — if the credentials are missing or the
package isn't installed, `push_to_sheet` returns a clear error string instead
of crashing the rest of the pipeline.
"""
from __future__ import annotations

from typing import Any

from bpa.config import get_settings
from bpa.logging_setup import get_logger

log = get_logger(__name__)


def _credentials_available() -> tuple[bool, str | None]:
    """Return (ok, error_message) — ok=True only if creds + spreadsheet id set."""
    settings = get_settings()
    if not settings.google_sheets_credentials_path:
        return False, "GOOGLE_SHEETS_CREDENTIALS_PATH not set"
    if not settings.google_sheets_spreadsheet_id:
        return False, "GOOGLE_SHEETS_SPREADSHEET_ID not set"
    return True, None


def push_to_sheet(
    records: list[dict[str, Any]],
    *,
    worksheet_name: str = "records",
    fields: tuple[str, ...] | None = None,
) -> tuple[bool, str]:
    """Push records to a Google Sheet. Returns (ok, message).

    On missing creds, returns (False, "skipped: <reason>") — the caller can
    log this and continue.
    """
    ok, err = _credentials_available()
    if not ok:
        log.warning("sheets.skipped", reason=err)
        return False, f"skipped: {err}"

    try:
        import gspread  # type: ignore
    except ImportError:
        msg = "gspread not installed; run `pip install gspread`"
        log.warning("sheets.skipped", reason=msg)
        return False, msg

    settings = get_settings()
    fields = fields or (
        "external_id",
        "name",
        "phone",
        "email",
        "address",
        "website",
        "price",
        "rating",
        "category",
        "scraped_at",
    )
    try:
        client = gspread.service_account(filename=settings.google_sheets_credentials_path)
        sh = client.open_by_key(settings.google_sheets_spreadsheet_id)
        try:
            ws = sh.worksheet(worksheet_name)
        except Exception:
            ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=len(fields))
        rows = [list(fields)]
        for rec in records:
            rows.append([str(rec.get(f, "")) for f in fields])
        ws.update(rows)
        log.info("sheets.pushed", count=len(records), sheet=worksheet_name)
        return True, f"pushed {len(records)} rows to {worksheet_name}"
    except Exception as exc:  # noqa: BLE001 — gspread raises many types
        msg = f"sheets push failed: {exc}"
        log.error("sheets.error", error=str(exc))
        return False, msg


__all__ = ["push_to_sheet"]