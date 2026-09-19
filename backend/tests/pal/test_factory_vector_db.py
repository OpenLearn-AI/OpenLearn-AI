"""P9-B factory tests: postgres branch of get_vector_db_provider.

Kept in a separate file so the existing test_factory.py stays untouched.
"""

from __future__ import annotations

import pytest

from app.config import settings
from app.pal.exceptions import ConfigurationError
from app.pal.factory import get_vector_db_provider
from app.pal.providers.vector_db.mock_provider import MockVectorDBProvider
from app.pal.providers.vector_db.postgres_provider import PostgresVectorDBProvider


def test_default_vector_db_provider_is_mock() -> None:
    assert isinstance(get_vector_db_provider(), MockVectorDBProvider)


def test_mock_provider_remains_explicitly_selectable() -> None:
    assert isinstance(get_vector_db_provider("mock"), MockVectorDBProvider)


def test_postgres_provider_without_session_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ai_vector_db_provider", "postgres")
    with pytest.raises(ConfigurationError, match="AsyncSession"):
        get_vector_db_provider()


def test_postgres_provider_with_session_is_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ai_vector_db_provider", "postgres")
    provider = get_vector_db_provider("postgres", session=object())
    assert isinstance(provider, PostgresVectorDBProvider)
