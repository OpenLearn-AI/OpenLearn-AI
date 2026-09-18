from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.pal.exceptions import ConfigurationError
from app.pal.interfaces.embedding import EmbeddingInterface
from app.pal.interfaces.ocr import OCRInterface
from app.pal.interfaces.reasoning import ReasoningInterface
from app.pal.interfaces.vector_db import VectorDBInterface
from app.pal.providers.embedding.bge_m3_provider import BGEM3EmbeddingProvider
from app.pal.providers.embedding.mock_provider import MockEmbeddingProvider
from app.pal.providers.ocr.gemini_provider import GeminiOCRProvider
from app.pal.providers.ocr.mock_provider import MockOCRProvider
from app.pal.providers.reasoning.mock_provider import MockReasoningProvider
from app.pal.providers.vector_db.mock_provider import MockVectorDBProvider
from app.pal.providers.vector_db.postgres_provider import PostgresVectorDBProvider


def get_ocr_provider(provider: str | None = None) -> OCRInterface:
    """Return the configured OCR provider."""
    provider_name = provider if provider is not None else settings.ai_ocr_provider
    if provider_name == "mock":
        return MockOCRProvider()
    if provider_name == "gemini":
        return GeminiOCRProvider()

    raise ConfigurationError(f"Unsupported OCR provider: {provider_name}")


def get_embedding_provider(
    provider: str | None = None,
    dimension: int | None = None,
) -> EmbeddingInterface:
    """Return the configured embedding provider."""
    provider_name = (
        provider if provider is not None else settings.ai_embedding_provider
    )
    dim = dimension if dimension is not None else settings.ai_embedding_dimension
    if provider_name == "mock":
        return MockEmbeddingProvider(dimension=dim)
    if provider_name == "bge-m3":
        return BGEM3EmbeddingProvider(dimension=dim)

    raise ConfigurationError(f"Unsupported embedding provider: {provider_name}")


def get_reasoning_provider(provider: str | None = None) -> ReasoningInterface:
    """Return the configured reasoning provider."""
    provider_name = (
        provider if provider is not None else settings.ai_reasoning_provider
    )
    if provider_name == "mock":
        return MockReasoningProvider()

    raise ConfigurationError(f"Unsupported reasoning provider: {provider_name}")


def get_vector_db_provider(
    provider: str | None = None,
    session: AsyncSession | None = None,
) -> VectorDBInterface:
    """Return the configured vector database provider.

    The postgres provider is session-backed: callers pass their
    request-scoped ``AsyncSession`` (e.g. from ``Depends(get_db)``).
    The mock provider needs no session.
    """
    provider_name = (
        provider if provider is not None else settings.ai_vector_db_provider
    )
    if provider_name == "mock":
        return MockVectorDBProvider()
    if provider_name == "postgres":
        if session is None:
            raise ConfigurationError(
                "Vector DB provider 'postgres' requires an AsyncSession."
            )
        return PostgresVectorDBProvider(session)

    raise ConfigurationError(f"Unsupported VectorDB provider: {provider_name}")
