"""SQLAlchemy persistence model for pgvector vector records (P9-B).

Provenance note: ``CanonicalDocument``/``Chunk`` are Pydantic domain models,
not database entities, so this table intentionally has NO foreign keys to
them. Document/chunk provenance (``document_id``, ``chunk_id``, pages, ...)
lives inside the JSONB ``metadata`` column, mirroring the PAL
``VectorRecord`` DTO contract.

The Python attribute for the JSONB column is ``metadata_`` because
``metadata`` is reserved by SQLAlchemy's Declarative API (``Base.metadata``);
the database column itself is named ``metadata`` as designed.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

#: Dense embedding dimension produced by BAAI/bge-m3 (P9-A). Fixed for
#: P9-B: the table column is VECTOR(1024) and every write is validated
#: against this constant (deliberately decoupled from
#: settings.ai_embedding_dimension so a config drift surfaces as an
#: explicit error instead of a silent DB failure).
EMBEDDING_DIMENSION = 1024


class VectorRecordModel(Base):
    """A stored dense embedding with JSONB provenance metadata."""

    __tablename__ = "vector_records"

    id: Mapped[str] = mapped_column(Text, primary_key=True)

    embedding: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_DIMENSION),
        nullable=False,
    )

    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
