from abc import abstractmethod
from typing import Any

from app.pal.interfaces.base import BasePALInterface
from app.pal.models.types import VectorRecord, VectorSearchResult


class VectorDBInterface(BasePALInterface):
    """Provider-independent vector database contract."""

    @abstractmethod
    async def upsert(
        self,
        records: list[VectorRecord],
    ) -> None:
        """Upsert a batch of vector records into the store."""
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        vector: list[float],
        *,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search the vector store using an embedding vector."""
        raise NotImplementedError

    @abstractmethod
    async def get(
        self,
        id: str,
    ) -> VectorRecord | None:
        """Retrieve a single vector record by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        *,
        ids: list[str] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """
        Delete vector records by specific IDs and/or matching metadata filters.

        Returns the count of deleted records.
        """
        raise NotImplementedError

