from collections.abc import Sequence

from app.pal.interfaces.embedding import EmbeddingInterface
from app.pal.models.types import EmbeddingResult, HealthStatus


class MockEmbeddingProvider(EmbeddingInterface):
    """Deterministic embedding provider for tests and local development."""

    provider_name = "mock"

    def __init__(self, dimension: int = 1024):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    async def health_check(self) -> HealthStatus:
        return HealthStatus(
            healthy=True,
            provider=self.provider_name,
            message="Mock embedding provider is ready.",
        )

    async def embed(self, text: str) -> EmbeddingResult:
        vector = [0.0] * self._dimension

        return EmbeddingResult(
            vector=vector,
            dimension=self._dimension,
            model="mock-embedding",
            provider=self.provider_name,
            metadata={"text_length": len(text)},
        )

    async def embed_batch(
        self,
        texts: Sequence[str],
    ) -> list[EmbeddingResult]:
        return [await self.embed(text) for text in texts]

