"""Request/response schemas for the Week 6 Course API (/v1/courses)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    """Payload for POST /v1/courses.

    Identity is never accepted from the client: ``owner_id`` is derived from
    the authenticated token, so unexpected fields are rejected (422).
    Title bounds mirror the ``courses.title`` varchar(255) column.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)


class CourseUpdate(BaseModel):
    """Full-replacement payload for PUT /v1/courses/{course_id}.

    Same contract as CourseCreate: PUT replaces title/description entirely,
    and ``owner_id`` cannot be changed by the client.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime