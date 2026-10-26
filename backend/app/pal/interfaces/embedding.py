from abc import abstractmethod
from collections.abc import Sequence

from app.pal.interfaces.base import BasePALInterface
from app.pal.models.types import EmbeddingResult


class EmbeddingInterface(BasePALInterface):
    """Provider-independent embedding contract."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector dimension produced by this embedding provider."""
        raise NotImplementedError

    @abstractmethod
    async def embed(
        self,
        text: str,
    ) -> EmbeddingResult:
        """Generate an embedding for the given text."""
        raise NotImplementedError

    @abstractmethod
    async def embed_batch(
        self,
        texts: Sequence[str],
    ) -> list[EmbeddingResult]:
        """Generate embeddings for a batch of texts."""
        raise NotImplementedError

