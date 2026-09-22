"""A material is an object stored in S3-compatible storage that belongs to a course.

Week 6 scope is the upload pipeline only: materials are registered with a
``pending`` status after the client uploads to a presigned URL. Content/virus
scanning and processing are explicitly a future phase, not implemented here.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Materials are registered as ``pending`` until a future scan/processing phase
# The supported status vocabulary is defined here; transitions are enforced
# by the material service.
PENDING_STATUS = "pending"
PROCESSING_STATUS = "processing"
READY_STATUS = "ready"
FAILED_STATUS = "failed"


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Server-generated object key inside the course's S3 namespace; never taken
    # from an arbitrary client-provided path. Unique so the same object cannot
    # be registered twice.
    s3_key: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=PENDING_STATUS,
        server_default=PENDING_STATUS,
        nullable=False,
    )

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("s3_key", name="uq_materials_s3_key"),
    )