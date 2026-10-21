"""One page of a material's extracted text (Week 9). Pages are 1-based;
empty pages are stored too."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

#: Page numbers stored in ``material_pages`` start at 1 (Week 9 decision).
MIN_MATERIAL_PAGE_NUMBER = 1


class MaterialPage(Base):
    """One page of extracted text belonging to a processed material."""

    __tablename__ = "material_pages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 1-based page number, matching the extraction contract (TS §11.3).
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Extracted page text; may be empty (empty pages are stored).
    text: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("material_id", "page_number", name="uq_material_pages_material_page"),
        CheckConstraint(
            f"page_number >= {MIN_MATERIAL_PAGE_NUMBER}",
            name="ck_material_pages_page_number_positive",
        ),
    )
