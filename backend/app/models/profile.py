import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Week 6 CSP subset (Tech Spec Section 15.1). The spec types education_level
    # and learning_style_vark as enums but defines no members yet, so Phase 1
    # keeps them free-form strings; value validation belongs to the API contract.
    education_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    major: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    university: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # v1.0 supports only English and Arabic (ISO 639-1, lowercase).
    preferred_language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        server_default="en",
        nullable=False,
    )

    learning_style_vark: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # No authoritative bound in the spec; 1440 is the physical minutes-per-day
    # ceiling. NULL is allowed until onboarding supplies a value.
    daily_available_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_profiles_user_id",
        ),
        CheckConstraint(
            "preferred_language IN ('en', 'ar')",
            name="ck_profiles_preferred_language_supported",
        ),
        CheckConstraint(
            "daily_available_minutes IS NULL OR "
            "(daily_available_minutes >= 1 AND daily_available_minutes <= 1440)",
            name="ck_profiles_daily_available_minutes_range",
        ),
    )
