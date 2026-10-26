"""PostgreSQL + pgvector vector store provider (P9-B).

Implements the frozen PAL ``VectorDBInterface`` contract on top of the
application's existing SQLAlchemy async stack (``AsyncSession`` +
``asyncpg``) and the ``pgvector`` SQLAlchemy integration.

Responsibility (PAL provider boundary per ADR-0009):

    VectorRecord(s) <-> PostgreSQL vector_records table (VECTOR(1024))

Design decisions:

* Sessions: the caller supplies the ``AsyncSession`` (e.g. the application's
  ``get_db`` dependency). The provider never creates engines or sessions.
* Transactions: the provider executes statements on the caller's session
  and never commits. The caller owns transaction boundaries (unit-of-work):
  nothing in the current architecture expects providers to commit
  request-scoped sessions, and per-operation commits would break
  multi-operation atomicity for the later retrieval layer (P9-C+).
* Upsert: a single multi-row ``INSERT ... ON CONFLICT (id) DO UPDATE`` built
  against the Core ``Table`` (``VectorRecordModel.__table__``), NOT the
  mapped class. Rationale: an ORM-entity insert enters SQLAlchemy's bulk
  path where string dict keys are resolved against class attributes; the
  key ``"metadata"`` would resolve to the inherited ``DeclarativeBase.metadata``
  (a ``MetaData`` object — the mapped attribute is ``metadata_``), which
  crashes bulk processing. Against the Core Table, ``"metadata"`` is simply
  a column name. ``created_at`` is preserved (never in the SET clause);
  ``updated_at`` is refreshed DB-side with ``func.now()`` in the conflict
  branch and filled by server default on insert.
* Similarity: exact cosine distance (``<=>``) with
  ``score = 1 - cosine_distance`` — for L2-normalized BGE-M3 vectors this
  equals cosine similarity in [-1, 1]. Exact search (no ANN index) is
  correct and fast at the expected P9-B scale; an HNSW index can be added
  later without any provider change.
* Filters: JSONB containment (``metadata @> filters``) — exact key/value
  matching for flat filters, sufficient for P9-B. No generic query language.
* Errors: existing PAL exceptions only. Invalid caller input (vector
  dimension, top_k, empty selectors/ids) -> ``InvalidInputError``; a
  misconfigured construction -> ``ConfigurationError``. No broad exception
  swallowing — health_check reports failures as an unhealthy status instead
  of raising, matching the PAL health contract.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import delete, func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vector_record import EMBEDDING_DIMENSION, VectorRecordModel
from app.pal.exceptions import ConfigurationError, InvalidInputError
from app.pal.interfaces.vector_db import VectorDBInterface
from app.pal.models.types import HealthStatus, VectorRecord, VectorSearchResult


class PostgresVectorDBProvider(VectorDBInterface):
    """pgvector-backed vector store bound to a caller-provided session."""

    provider_name = "postgres"

    def __init__(self, session: AsyncSession) -> None:
        if session is None:
            raise ConfigurationError(
                "PostgresVectorDBProvider requires an AsyncSession."
            )
        self._session = session

    async def upsert(self, records: list[VectorRecord]) -> None:
        """Insert new records / update existing ones by primary key.

        One batched multi-row statement: existing rows get embedding,
        content, metadata and ``updated_at`` refreshed; ``created_at`` is
        preserved by the conflict clause. An empty list is a harmless
        no-op. Nothing is committed (caller owns the transaction).
        """
        if not records:
            return
        values: list[dict[str, Any]] = []
        for record in records:
            if not record.id:
                raise InvalidInputError(
                    "VectorRecord.id must be a non-empty string."
                )
            self._validate_vector(record.vector)
            values.append(
                {
                    "id": record.id,
                    "embedding": record.vector,
                    "content": record.content,
                    "metadata": record.metadata,
                }
            )

        # Target the Core Table, not the mapped class: string keys must
        # resolve against table columns (see module docstring for why the
        # ORM-entity insert path is unsafe with the reserved "metadata" key).
        table = VectorRecordModel.__table__
        stmt = pg_insert(table).values(values)
        excluded = stmt.excluded
        stmt = stmt.on_conflict_do_update(
            index_elements=[table.c.id],
            set_={
                "embedding": excluded["embedding"],
                "content": excluded["content"],
                "metadata": excluded["metadata"],
                "updated_at": func.now(),
            },
        )
        await self._session.execute(stmt)

    async def search(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Return up to ``top_k`` records nearest to ``vector`` by cosine.

        Score is ``1 - cosine_distance`` (cosine similarity for normalized
        vectors), highest first. Ordering happens in PostgreSQL via
        ``ORDER BY embedding <=> :vector``. An empty ``filters`` dict is
        treated as "no filter".
        """
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise InvalidInputError(
                f"top_k must be a positive integer, got {top_k!r}."
            )
        self._validate_vector(vector)

        distance = VectorRecordModel.embedding.cosine_distance(vector)
        stmt = (
            select(VectorRecordModel, distance.label("distance"))
            .order_by(distance.asc())
            .limit(top_k)
        )
        if filters:
            stmt = stmt.where(VectorRecordModel.metadata_.contains(filters))

        result = await self._session.execute(stmt)
        return [
            VectorSearchResult(
                id=record.id,
                score=1.0 - float(db_distance),
                content=record.content,
                metadata=record.metadata_,
            )
            for record, db_distance in result.all()
        ]

    async def get(self, id: str) -> VectorRecord | None:
        """Return the stored record for ``id``, or None if absent."""
        if not id:
            raise InvalidInputError("Vector record id must be a non-empty string.")
        record = await self._session.get(VectorRecordModel, id)
        if record is None:
            return None
        # pgvector may hand back a numpy array depending on version —
        # list() normalizes it to plain floats for the DTO either way.
        return VectorRecord(
            id=record.id,
            vector=list(record.embedding),
            content=record.content,
            metadata=record.metadata_,
        )

    async def delete(
        self,
        *,
        ids: list[str] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """Delete by ids and/or metadata filters; returns deleted count.

        Calling with neither (or an empty ids list and no filters) raises
        ``InvalidInputError`` — this provider refuses to delete a whole
        table by accident. An empty ``filters`` dict counts as "no filter".
        """
        if not ids and not filters:
            raise InvalidInputError(
                "delete() requires ids and/or filters; refusing to delete "
                "the entire vector_records table."
            )
        stmt = delete(VectorRecordModel)
        if ids:
            stmt = stmt.where(VectorRecordModel.id.in_(ids))
        if filters:
            stmt = stmt.where(VectorRecordModel.metadata_.contains(filters))
        result = await self._session.execute(stmt)
        return int(result.rowcount or 0)

    async def health_check(self) -> HealthStatus:
        """Cheap liveness probe (SELECT 1) — never scans vector data."""
        try:
            await self._session.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            return HealthStatus(
                healthy=False,
                provider=self.provider_name,
                message=f"PostgreSQL vector store is unreachable: {exc}",
            )
        return HealthStatus(
            healthy=True,
            provider=self.provider_name,
            message="PostgreSQL pgvector store is reachable.",
        )

    @staticmethod
    def _validate_vector(vector: list[float]) -> None:
        if len(vector) != EMBEDDING_DIMENSION:
            raise InvalidInputError(
                f"Vector dimension mismatch: expected {EMBEDDING_DIMENSION}, "
                f"got {len(vector)}."
            )
