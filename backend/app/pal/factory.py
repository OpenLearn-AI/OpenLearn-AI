from app.config import settings
from app.pal.exceptions import ConfigurationError
from app.pal.interfaces.embedding import EmbeddingInterface
from app.pal.interfaces.ocr import OCRInterface
from app.pal.interfaces.reasoning import ReasoningInterface
from app.pal.interfaces.vector_db import VectorDBInterface
from app.pal.providers.embedding.mock_provider import MockEmbeddingProvider
from app.pal.providers.ocr.mock_provider import MockOCRProvider
from app.pal.providers.reasoning.mock_provider import MockReasoningProvider
from app.pal.providers.vector_db.mock_provider import MockVectorDBProvider


def get_ocr_provider(provider: str | None = None) -> OCRInterface:
    """Return the configured OCR provider."""
    provider_name = provider if provider is not None else settings.ai_ocr_provider
    if provider_name == "mock":
        return MockOCRProvider()

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

    raise ConfigurationError(f"Unsupported embedding provider: {provider_name}")


def get_reasoning_provider(provider: str | None = None) -> ReasoningInterface:
    """Return the configured reasoning provider."""
    provider_name = (
        provider if provider is not None else settings.ai_reasoning_provider
    )
    if provider_name == "mock":
        return MockReasoningProvider()

    raise ConfigurationError(f"Unsupported reasoning provider: {provider_name}")


def get_vector_db_provider(provider: str | None = None) -> VectorDBInterface:
    """Return the configured vector database provider."""
    provider_name = (
        provider if provider is not None else settings.ai_vector_db_provider
    )
    if provider_name == "mock":
        return MockVectorDBProvider()

    raise ConfigurationError(f"Unsupported VectorDB provider: {provider_name}")

