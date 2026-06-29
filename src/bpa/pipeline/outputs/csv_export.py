"""CSV export — writes normalized records to a CSV file.

Synchronous because CSV writing is CPU-bound and the file ends up on disk.
"""
from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_FIELDS = (
    "target_id",
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
    "source_url",
)


def export_csv(
    records: list[dict[str, Any]],
    output_path: str | Path,
    *,
    fields: tuple[str, ...] = DEFAULT_FIELDS,
) -> Path:
    """Write records to CSV. Returns the absolute path written."""
    path = Path(output_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            row: dict[str, Any] = {}
            for field_name in fields:
                value = rec.get(field_name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, (dict, list)):
                    value = str(value)
                row[field_name] = value if value is not None else ""
            writer.writerow(row)
    return path


def default_csv_path(target_name: str, *, base_dir: str | Path | None = None) -> Path:
    """Build a timestamped CSV path under the configured output dir."""
    from bpa.config import get_settings

    settings = get_settings()
    base = Path(base_dir) if base_dir else Path(settings.csv_output_dir)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in target_name)
    return base / f"{safe_name}-{ts}.csv"


__all__ = ["DEFAULT_FIELDS", "default_csv_path", "export_csv"]