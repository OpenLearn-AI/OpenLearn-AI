"""Request/response schemas for the Week 6 material upload pipeline.

POST /v1/courses/{course_id}/materials/upload-url
POST /v1/courses/{course_id}/materials
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
    course_id: uuid.UUID
    title: str
    s3_key: str
    upload_url: str
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
    status: str
    uploaded_by: uuid.UUID
    created_at: datetime