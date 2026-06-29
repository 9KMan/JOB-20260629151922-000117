"""Pydantic v2 schemas for normalized records."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from bpa.pipeline.parsers.normalize import (
    clean_text,
    coerce_date,
    coerce_decimal,
    coerce_float,
    coerce_int,
    make_external_id,
    normalize_email,
    normalize_phone,
    normalize_url,
)


class NormalizedRecord(BaseModel):
    """A normalized business record ready for upsert.

    Field names use snake_case (API-friendly); the DB column names match.
    For external systems where DB columns diverge, use `alias=` on the
    target-specific subclass below.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
        populate_by_name=True,
    )

    name: str = Field(..., min_length=1, description="Business name")
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    website: str | None = None
    price: float | None = None
    rating: float | None = None
    category: str | None = None
    external_id: str = Field(..., min_length=1, description="Source dedup key")
    raw: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name", mode="before")
    @classmethod
    def _clean_name(cls, v: Any) -> str:
        cleaned = clean_text(v)
        if not cleaned:
            raise ValueError("name must not be empty")
        return cleaned

    @field_validator("phone", mode="before")
    @classmethod
    def _clean_phone(cls, v: Any) -> str | None:
        return normalize_phone(v)

    @field_validator("email", mode="before")
    @classmethod
    def _clean_email(cls, v: Any) -> str | None:
        return normalize_email(v)

    @field_validator("website", mode="before")
    @classmethod
    def _clean_website(cls, v: Any) -> str | None:
        return normalize_url(v)

    @field_validator("price", "rating", mode="before")
    @classmethod
    def _coerce_numbers(cls, v: Any) -> float | None:
        return coerce_float(v)

    @classmethod
    def from_raw(cls, raw: dict[str, Any], *, id_fields: tuple[str, ...] = ("name",)) -> "NormalizedRecord":
        """Construct from a raw scraped dict.

        `id_fields` names the raw dict keys to combine into the external_id.
        Unknown keys are kept in `raw`.
        """
        # Build external_id from the chosen raw fields, with a fallback to row index
        ext = make_external_id(*(raw.get(f) for f in id_fields))
        if not ext:
            ext = make_external_id(raw.get("external_id"), raw.get("name"))
        if not ext:
            raise ValueError("could not derive external_id from raw record")
        data = {
            "name": raw.get("name") or raw.get("title"),
            "phone": raw.get("phone") or raw.get("tel"),
            "email": raw.get("email"),
            "address": raw.get("address") or raw.get("location"),
            "website": raw.get("website") or raw.get("url"),
            "price": coerce_decimal(raw.get("price")),
            "rating": raw.get("rating"),
            "category": raw.get("category"),
            "external_id": ext,
            "raw": dict(raw),
        }
        return cls(**data)


class DBRecord(BaseModel):
    """Shape of a row in the records table.

    Uses `alias=` because the DB column `external_id` and the API field
    `externalId` differ; this lets the same Pydantic model serialize cleanly
    to both JSON APIs and DB rows.
    """

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int | None = Field(default=None)
    target_id: int
    external_id: str = Field(..., alias="externalId")
    payload: dict[str, Any]
    source_url: str | None = Field(default=None, alias="sourceUrl")
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_db_dict(self) -> dict[str, Any]:
        """Return a dict with DB column names (camelCase → snake_case mapping)."""
        return {
            "id": self.id,
            "target_id": self.target_id,
            "external_id": self.external_id,
            "payload": self.payload,
            "source_url": self.source_url,
            "scraped_at": self.scraped_at,
        }