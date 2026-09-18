"""P9-B model tests: vector_records table shape (metadata only, no DB)."""

from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateColumn

from app.db.base import Base
from app.models import VectorRecordModel  # noqa: F401 — registers metadata
from app.models.vector_record import EMBEDDING_DIMENSION


def test_vector_records_table_is_registered_in_metadata() -> None:
    assert "vector_records" in Base.metadata.tables


def test_embedding_column_is_vector_1024_not_null() -> None:
    col = VectorRecordModel.__table__.c.embedding
    assert isinstance(col.type, Vector)
    assert col.nullable is False
    ddl = str(CreateColumn(col).compile(dialect=postgresql.dialect())).upper()
    assert f"VECTOR({EMBEDDING_DIMENSION})" in ddl


def test_metadata_column_is_jsonb_named_metadata() -> None:
    col = VectorRecordModel.__table__.c["metadata"]
    assert isinstance(col.type, postgresql.JSONB)
    assert col.name == "metadata"
    assert col.nullable is False
    assert col.server_default is not None  # '{}'::jsonb


def test_id_is_text_primary_key_and_content_is_nullable() -> None:
    id_col = VectorRecordModel.__table__.c.id
    assert id_col.primary_key is True
    assert isinstance(id_col.type, Text)
    assert VectorRecordModel.__table__.c.content.nullable is True


def test_timestamps_are_tz_aware_with_server_defaults() -> None:
    for name in ("created_at", "updated_at"):
        col = VectorRecordModel.__table__.c[name]
        assert col.nullable is False
        assert col.type.timezone is True
        assert col.server_default is not None
