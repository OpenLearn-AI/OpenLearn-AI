"""P9-B unit tests for PostgresVectorDBProvider (no real database).

A deterministic FakeAsyncSession records executed statements and returns
canned results, so validation, upsert semantics (compiled SQL), DTO mapping
and PAL error behavior are verified offline. Real SQL behavior (cosine
ordering, JSONB filtering, rowcounts, upsert persistence) is covered by the
separated integration test file.

Regression coverage: the upsert tests assert the Core-Table-targeted
statement (``INSERT ... ON CONFLICT (id) DO UPDATE`` including
``metadata = excluded.metadata``), guarding against a reintroduction of the
ORM-entity insert that crashes on the reserved ``metadata`` attribute name.
"""

from __future__ import annotations

from collections import namedtuple
from typing import Any

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError

from app.models.vector_record import EMBEDDING_DIMENSION
from app.pal.exceptions import ConfigurationError, InvalidInputError
from app.pal.models.types import VectorRecord
from app.pal.providers.vector_db.postgres_provider import PostgresVectorDBProvider

_DIM = EMBEDDING_DIMENSION

Row = namedtuple("Row", ["record", "distance"])

_UNSET = object()


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeResult:
    def __init__(self, rows: list[Any] | None = None, rowcount: int = 0) -> None:
        self._rows = rows if rows is not None else []
        self.rowcount = rowcount

    def all(self) -> list[Any]:
        return list(self._rows)


class FakeAsyncSession:
    def __init__(
        self,
        result: FakeResult | None = None,
        get_result: Any = _UNSET,
    ) -> None:
        self.executed: list[tuple[Any, Any]] = []
        self.get_calls: list[tuple[type, str]] = []
        self._result = result
        self._get_result = get_result

    async def execute(self, statement: Any, parameters: Any = None) -> FakeResult:
        self.executed.append((statement, parameters))
        return self._result if self._result is not None else FakeResult()

    async def get(self, model: type, key: str) -> Any:
        self.get_calls.append((model, key))
        return None if self._get_result is _UNSET else self._get_result


class FailingSession(FakeAsyncSession):
    async def execute(self, statement: Any, parameters: Any = None) -> FakeResult:
        raise SQLAlchemyError("connection refused")


class FakeModelRow:
    """Mimics a VectorRecordModel instance loaded from the database."""

    def __init__(
        self,
        id: str,
        embedding: list[float],
        content: str | None,
        metadata: dict[str, Any],
    ) -> None:
        self.id = id
        self.embedding = embedding
        self.content = content
        self.metadata_ = metadata


def _vector(value: float = 0.5) -> list[float]:
    return [value] * _DIM


def _provider(session: FakeAsyncSession) -> PostgresVectorDBProvider:
    return PostgresVectorDBProvider(session)  # type: ignore[arg-type]


def _compiled(statement: Any) -> tuple[str, dict[str, Any]]:
    compiled = statement.compile(dialect=postgresql.dialect())
    return str(compiled), dict(compiled.params)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construction_accepts_session() -> None:
    provider = _provider(FakeAsyncSession())
    assert provider.provider_name == "postgres"


def test_construction_requires_session() -> None:
    with pytest.raises(ConfigurationError, match="AsyncSession"):
        PostgresVectorDBProvider(session=None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# upsert
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_upsert_is_harmless_noop() -> None:
    session = FakeAsyncSession()
    await _provider(session).upsert([])
    assert session.executed == []


@pytest.mark.asyncio
async def test_upsert_executes_single_upsert_statement_and_does_not_mutate_input() -> None:
    session = FakeAsyncSession()
    records = [
        VectorRecord(
            id="doc-123:0",
            vector=_vector(1.0),
            content="first",
            metadata={"document_id": "doc-123"},
        ),
        VectorRecord(id="doc-123:1", vector=_vector(0.5), content=None, metadata={}),
    ]
    snapshot = [r.model_copy() for r in records]

    await _provider(session).upsert(records)

    assert len(session.executed) == 1
    statement, parameters = session.executed[0]
    sql, params = _compiled(statement)
    assert "INSERT INTO vector_records" in sql
    # Core-Table-targeted upsert semantics (regression: ORM-entity insert
    # crashed on the reserved "metadata" attribute name).
    assert "ON CONFLICT (id) DO UPDATE SET" in sql
    assert "embedding = excluded.embedding" in sql
    assert "content = excluded.content" in sql
    assert "metadata = excluded.metadata" in sql
    assert "updated_at = now()" in sql
    assert "created_at" not in sql  # preserved by the conflict clause
    assert "doc-123:0" in str(params.values())  # both records in one statement
    assert parameters is None  # values bound via the statement, not execute()
    assert records == snapshot  # caller input untouched


@pytest.mark.asyncio
async def test_upsert_rejects_wrong_dimension_without_db_call() -> None:
    session = FakeAsyncSession()
    with pytest.raises(InvalidInputError, match="dimension"):
        await _provider(session).upsert(
            [VectorRecord(id="x:0", vector=[0.1, 0.2])]
        )
    assert session.executed == []


@pytest.mark.asyncio
async def test_upsert_rejects_empty_id() -> None:
    session = FakeAsyncSession()
    with pytest.raises(InvalidInputError, match="non-empty"):
        await _provider(session).upsert([VectorRecord(id="", vector=_vector())])
    assert session.executed == []


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_existing_returns_vector_record() -> None:
    stored = FakeModelRow(
        id="doc-123:0",
        embedding=_vector(),
        content="chunk text",
        metadata={"document_id": "doc-123", "pages": [1, 2]},
    )
    session = FakeAsyncSession(get_result=stored)

    result = await _provider(session).get("doc-123:0")

    assert result == VectorRecord(
        id="doc-123:0",
        vector=_vector(),
        content="chunk text",
        metadata={"document_id": "doc-123", "pages": [1, 2]},
    )
    assert session.get_calls and session.get_calls[0][1] == "doc-123:0"


@pytest.mark.asyncio
async def test_get_missing_returns_none() -> None:
    session = FakeAsyncSession()  # get_result unset -> None
    assert await _provider(session).get("ghost:0") is None


@pytest.mark.asyncio
async def test_get_rejects_empty_id() -> None:
    session = FakeAsyncSession()
    with pytest.raises(InvalidInputError, match="non-empty"):
        await _provider(session).get("")
    assert session.get_calls == []


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_maps_rows_computes_scores_and_keeps_db_order() -> None:
    near = FakeModelRow("d:0", _vector(), "near", {"document_id": "d"})
    mid = FakeModelRow("d:1", _vector(), "mid", {"document_id": "d"})
    far = FakeModelRow("d:2", _vector(), "far", {"document_id": "d"})
    # Rows already ordered by ascending cosine distance, as PostgreSQL does.
    session = FakeAsyncSession(
        result=FakeResult(rows=[Row(near, 0.0), Row(mid, 0.2), Row(far, 1.5)])
    )
    query = _vector()

    results = await _provider(session).search(query)

    assert [r.id for r in results] == ["d:0", "d:1", "d:2"]
    assert results[0].score == pytest.approx(1.0)
    assert results[1].score == pytest.approx(0.8)
    assert results[2].score == pytest.approx(-0.5)
    assert all(r.metadata == {"document_id": "d"} for r in results)
    assert query == _vector()  # query vector not mutated

    sql, _ = _compiled(session.executed[0][0])
    assert "<=>" in sql  # pgvector cosine distance operator
    assert "ORDER BY" in sql
    assert "LIMIT" in sql


@pytest.mark.parametrize("bad_top_k", [0, -1, 2.5, "3", True])
@pytest.mark.asyncio
async def test_search_rejects_invalid_top_k(bad_top_k: Any) -> None:
    session = FakeAsyncSession()
    with pytest.raises(InvalidInputError, match="top_k"):
        await _provider(session).search(_vector(), top_k=bad_top_k)
    assert session.executed == []


@pytest.mark.asyncio
async def test_search_rejects_wrong_dimension() -> None:
    session = FakeAsyncSession()
    with pytest.raises(InvalidInputError, match="dimension"):
        await _provider(session).search([0.1, 0.2])
    assert session.executed == []


@pytest.mark.asyncio
async def test_search_applies_metadata_filters_as_jsonb_containment() -> None:
    session = FakeAsyncSession(result=FakeResult(rows=[]))

    await _provider(session).search(
        _vector(), top_k=3, filters={"document_id": "doc-123"}
    )

    sql, params = _compiled(session.executed[0][0])
    assert "@>" in sql  # metadata @> filters
    assert any(
        value == {"document_id": "doc-123"}
        for value in params.values()
        if isinstance(value, dict)
    )


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_by_ids_returns_deleted_count() -> None:
    session = FakeAsyncSession(result=FakeResult(rowcount=2))

    deleted = await _provider(session).delete(ids=["d:0", "d:1"])

    assert deleted == 2
    sql, _ = _compiled(session.executed[0][0])
    assert "DELETE FROM vector_records" in sql
    assert "IN" in sql


@pytest.mark.asyncio
async def test_delete_by_metadata_filters_returns_count() -> None:
    session = FakeAsyncSession(result=FakeResult(rowcount=3))

    deleted = await _provider(session).delete(filters={"document_id": "doc-123"})

    assert deleted == 3
    sql, _ = _compiled(session.executed[0][0])
    assert "DELETE FROM vector_records" in sql
    assert "@>" in sql


@pytest.mark.asyncio
async def test_delete_combines_ids_and_filters() -> None:
    session = FakeAsyncSession(result=FakeResult(rowcount=1))

    await _provider(session).delete(ids=["d:0"], filters={"document_id": "d"})

    sql, _ = _compiled(session.executed[0][0])
    assert "IN" in sql and "@>" in sql


@pytest.mark.asyncio
async def test_delete_without_selector_raises_and_never_touches_db() -> None:
    session = FakeAsyncSession()
    with pytest.raises(InvalidInputError, match="ids and/or filters"):
        await _provider(session).delete()
    assert session.executed == []


# ---------------------------------------------------------------------------
# health_check
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check_healthy_when_database_reachable() -> None:
    status = await _provider(FakeAsyncSession()).health_check()
    assert status.healthy is True
    assert status.provider == "postgres"


@pytest.mark.asyncio
async def test_health_check_reports_unreachable_database() -> None:
    status = await _provider(FailingSession()).health_check()
    assert status.healthy is False
    assert "unreachable" in (status.message or "")
