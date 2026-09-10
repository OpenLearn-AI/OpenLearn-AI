import uuid
from typing import Any

from sqlalchemy import String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    keycloak_issuer: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    keycloak_subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    email_verified: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        nullable=False,
    )

    preferred_lang: Mapped[str] = mapped_column(
        String(10),
        default="en",
        server_default="en",
        nullable=False,
    )

    settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "keycloak_issuer",
            "keycloak_subject",
            name="uq_users_keycloak_identity",
        ),
    )

