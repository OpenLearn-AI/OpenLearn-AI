from abc import abstractmethod
from typing import Any

from app.pal.interfaces.base import BasePALInterface
from app.pal.models.types import RankingResult, VectorSearchResult


class RankingInterface(BasePALInterface):
    """Provider-independent ranking contract (deferred implementation)."""

    @abstractmethod
    async def rank(
        self,
        query: str,
        candidates: list[VectorSearchResult] | list[dict[str, Any]],
        *,
        top_k: int | None = None,
    ) -> list[RankingResult]:
        """Rank candidate results against the query."""
        raise NotImplementedError

