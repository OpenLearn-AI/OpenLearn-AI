"""Request/response schemas for the Week 6 Profile API (GET/PUT /v1/users/me)."""

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# v1.0 supports only English and Arabic (ISO 639-1, lowercase). This mirrors
# the ck_profiles_preferred_language_supported database constraint.
SupportedLanguage = Literal["en", "ar"]


class ProfileUpdate(BaseModel):
    """Full-replacement profile payload for PUT /v1/users/me.

    Unexpected fields are rejected (422): identity comes exclusively from the
    authenticated token, so a client-supplied user_id must never be accepted.

    education_level and learning_style_vark are free-form strings: the spec
    types them as enums but defines no members yet. String bounds mirror the
    database column sizes so invalid payloads are rejected with 422 instead of
    surfacing as database errors.
    """

    model_config = ConfigDict(extra="forbid")

    education_level: str = Field(min_length=1, max_length=50)
    major: str = Field(min_length=1, max_length=255)
    preferred_language: SupportedLanguage
    university: str | None = Field(default=None, min_length=1, max_length=255)
    learning_style_vark: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )
    # Required and positive per the Week 6 contract; capped at 1440 to mirror
    # the approved ck_profiles_daily_available_minutes_range database constraint.
    # Strict typing rejects booleans (Pydantic would otherwise coerce true -> 1).
    daily_available_minutes: int = Field(
        strict=True,
        gt=0,
        le=1440,
    )


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    education_level: str
    major: str
    preferred_language: str
    university: str | None
    learning_style_vark: str | None
    daily_available_minutes: int
