"""A material is an object stored in S3-compatible storage that belongs to a course.

Week 6 scope is the upload pipeline only: materials are registered with a
``pending`` status after the client uploads to a presigned URL. Content/virus
scanning and processing are explicitly a future phase, not implemented here.

Week 9: ``sha256`` (server-computed content hash, unique per course) and
``retry_count`` (manual retries used, max ``MATERIAL_RETRY_LIMIT``).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

#: Manual retries allowed beyond the initial processing attempt (Week 9).
MATERIAL_RETRY_LIMIT = 3

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

    # Content hash; NULL only for pre-Week 9 rows (NULLs never collide).
    sha256: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    # ETag of the object version hashed at registration; processing reads with
    # If-Match so a replaced object is rejected (NULL for older rows).
    s3_etag: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    # Manual retries consumed beyond the initial processing attempt.
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )

    # Last change of the row (status moves included); the stuck-material
    # reaper compares it with the timeout.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("s3_key", name="uq_materials_s3_key"),
        UniqueConstraint("course_id", "sha256", name="uq_materials_course_sha256"),
        CheckConstraint(
            "status IN ('pending', 'processing', 'ready', 'failed')",
            name="ck_materials_status_supported",
        ),
    )