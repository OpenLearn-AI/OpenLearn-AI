"""Request/response schemas for the Course API (/v1/courses)."""

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


# PUT /v1/courses/{course_id} takes the same contract as creation: it replaces
# title/description entirely and can never change ``owner_id``, so both
# operations share one request schema. Aliased rather than subclassed so the
# PUT body stays identical to the POST body, field for field.
CourseUpdate = CourseCreate


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime