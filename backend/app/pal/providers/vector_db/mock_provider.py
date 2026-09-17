import math
from typing import Any

from app.pal.exceptions import InvalidInputError
from app.pal.interfaces.vector_db import VectorDBInterface
from app.pal.models.types import HealthStatus, VectorRecord, VectorSearchResult


class MockVectorDBProvider(VectorDBInterface):
    """Deterministic in-memory vector database provider for testing."""

    provider_name = "mock"

    def __init__(self):
        self._records: dict[str, VectorRecord] = {}

    async def health_check(self) -> HealthStatus:
        return HealthStatus(
            healthy=True,
            provider=self.provider_name,
            message="Mock VectorDB provider is ready.",
        )

    async def upsert(self, records: list[VectorRecord]) -> None:
        for record in records:
            self._records[record.id] = record

    async def get(self, id: str) -> VectorRecord | None:
        return self._records.get(id)

    async def search(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        results: list[VectorSearchResult] = []
        norm_q = math.sqrt(sum(a * a for a in vector))

        for record in self._records.values():
            if filters:
                match = True
                for k, v in filters.items():
                    if record.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            if len(vector) != len(record.vector):
                raise InvalidInputError(
                    f"Query vector dimension ({len(vector)}) does not match stored vector dimension "
                    f"({len(record.vector)}) for record '{record.id}'."
                )

            norm_r = math.sqrt(sum(b * b for b in record.vector))
            if norm_q == 0.0 or norm_r == 0.0:
                score = 0.0
            else:
                dot = sum(a * b for a, b in zip(vector, record.vector, strict=True))
                score = float(dot / (norm_q * norm_r))

            results.append(
                VectorSearchResult(
                    id=record.id,
                    score=score,
                    content=record.content,
                    metadata=record.metadata,
                )
            )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    async def delete(
        self,
        *,
        ids: list[str] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> int:
        to_delete: set[str] = set()

        if ids:
            to_delete.update(i for i in ids if i in self._records)

        if filters:
            for record_id, record in self._records.items():
                match = True
                for k, v in filters.items():
                    if record.metadata.get(k) != v:
                        match = False
                        break
                if match:
                    to_delete.add(record_id)

        for record_id in to_delete:
            self._records.pop(record_id, None)

        return len(to_delete)

