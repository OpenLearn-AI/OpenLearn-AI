"""Request/response schemas for the Week 6 material upload pipeline.

POST /v1/courses/{course_id}/materials/upload-url
POST /v1/courses/{course_id}/materials
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MaterialStatus = Literal["pending", "processing", "ready", "failed"]


class UploadUrlCreate(BaseModel):
    """Payload for the presigned-URL endpoint.

    Only the minimum metadata required to build a server-side key and carry
    the material title is accepted; identity and the object key are never
    client-controlled.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    filename: str = Field(min_length=1, max_length=255)


class UploadUrlResponse(BaseModel):
    """Presigned POST upload target.

    The client sends a ``multipart/form-data`` POST to ``upload_url`` with every
    entry of ``upload_fields`` as a form field, followed by the file as the
    last field named ``file``. Storage rejects files larger than
    ``max_size_bytes``.
    """

    course_id: uuid.UUID
    title: str
    s3_key: str
    upload_url: str
    upload_fields: dict[str, str]
    max_size_bytes: int
    expires_in: int


class MaterialCreate(BaseModel):
    """Payload for registering a material after the direct upload completes.

    ``s3_key`` must be the one returned by the upload-url flow for this course;
    the endpoint validates it stays inside the course's material namespace.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    s3_key: str = Field(min_length=1, max_length=1024)


class MaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    s3_key: str
    status: MaterialStatus
    uploaded_by: uuid.UUID
    created_at: datetime


class MaterialStatusResponse(BaseModel):
    material_id: uuid.UUID
    status: MaterialStatus


class MaterialPageResponse(BaseModel):
    """One stored page of extracted text (1-based; text may be empty)."""

    page_number: int = Field(
        ge=1,
        description="1-based page number within the processed document.",
    )
    text: str = Field(description="Extracted text of the page.")


class MaterialPagesResponse(BaseModel):
    """A material's stored pages in ascending order; empty until processed."""

    material_id: uuid.UUID
    pages: list[MaterialPageResponse]


class MaterialAcceptedResponse(BaseModel):
    material_id: uuid.UUID
    job_id: str | None = Field(
        default=None,
        description=(
            "Celery task id for a freshly enqueued processing job. ``None`` "
            "when an existing material was reused (no new job). Intended for "
            "log correlation only in W7; it is not queryable through the API."
        ),
    )
    status: MaterialStatus = Field(
        description=(
            "``pending`` for a new or retried material, otherwise the "
            "existing material's current status."
        )
    )
