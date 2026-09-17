import pytest

from app.config import settings
from app.pal.exceptions import ConfigurationError
from app.pal.factory import (
    get_embedding_provider,
    get_ocr_provider,
    get_reasoning_provider,
    get_vector_db_provider,
)
from app.pal.providers.embedding.mock_provider import MockEmbeddingProvider
from app.pal.providers.ocr.mock_provider import MockOCRProvider
from app.pal.providers.reasoning.mock_provider import MockReasoningProvider
from app.pal.providers.vector_db.mock_provider import MockVectorDBProvider


def test_get_ocr_provider_defaults_to_config():
    provider = get_ocr_provider()
    assert isinstance(provider, MockOCRProvider)


def test_get_ocr_provider_explicit():
    provider = get_ocr_provider("mock")
    assert isinstance(provider, MockOCRProvider)


def test_get_embedding_provider_defaults_to_config():
    provider = get_embedding_provider()
    assert isinstance(provider, MockEmbeddingProvider)
    assert provider.dimension == settings.ai_embedding_dimension


def test_get_embedding_provider_explicit():
    provider = get_embedding_provider("mock", dimension=768)
    assert isinstance(provider, MockEmbeddingProvider)
    assert provider.dimension == 768


def test_get_reasoning_provider_defaults_to_config():
    provider = get_reasoning_provider()
    assert isinstance(provider, MockReasoningProvider)


def test_get_reasoning_provider_explicit():
    provider = get_reasoning_provider("mock")
    assert isinstance(provider, MockReasoningProvider)


def test_get_vector_db_provider_defaults_to_config():
    provider = get_vector_db_provider()
    assert isinstance(provider, MockVectorDBProvider)


def test_get_vector_db_provider_explicit():
    provider = get_vector_db_provider("mock")
    assert isinstance(provider, MockVectorDBProvider)


def test_unsupported_ocr_provider_raises_configuration_error():
    with pytest.raises(ConfigurationError, match="Unsupported OCR provider"):
        get_ocr_provider("does-not-exist")


def test_unsupported_embedding_provider_raises_configuration_error():
    with pytest.raises(ConfigurationError, match="Unsupported embedding provider"):
        get_embedding_provider("does-not-exist")


def test_unsupported_reasoning_provider_raises_configuration_error():
    with pytest.raises(ConfigurationError, match="Unsupported reasoning provider"):
        get_reasoning_provider("does-not-exist")


def test_unsupported_vector_db_provider_raises_configuration_error():
    with pytest.raises(ConfigurationError, match="Unsupported VectorDB provider"):
        get_vector_db_provider("does-not-exist")
