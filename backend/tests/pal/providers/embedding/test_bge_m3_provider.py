"""P9-A tests: BGE-M3 embedding provider against the frozen PAL contract.

No model downloads: the ``sentence_transformers`` and ``torch`` module
namespaces are replaced with deterministic in-process fakes (the provider
imports them lazily inside its load path, so sys.modules fakes are picked
up). Lazy loading, device resolution, encode invocation, PAL error mapping,
ordering and the async boundary are verified without the real ML stack.
No network, no downloads, no GPU required.
"""

from __future__ import annotations

import sys
import threading
import types
from collections.abc import Sequence
from types import SimpleNamespace
from typing import Any

import pytest
import requests

from app.config import settings
from app.pal.exceptions import (
    ConfigurationError,
    InvalidInputError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.pal.factory import get_embedding_provider
from app.pal.models.types import EmbeddingResult
from app.pal.providers.embedding.bge_m3_provider import BGEM3EmbeddingProvider

_MODEL = "BAAI/bge-m3"
_DIM = 1024


class FakeOutOfMemoryError(RuntimeError):
    """Stand-in for torch.cuda.OutOfMemoryError in the fake torch module."""


class FakeArray:
    """Minimal ndarray stand-in: ``.shape`` plus row indexing with ``.tolist()``."""

    def __init__(self, rows: list[list[float]]) -> None:
        self._rows = rows
        self.shape = (len(rows), len(rows[0]) if rows else 0)

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, index: int) -> Any:
        row = self._rows[index]
        return SimpleNamespace(tolist=lambda: list(row))


class FakeSentenceTransformer:
    """Deterministic SentenceTransformer stand-in recording all interactions."""

    constructions: list[dict[str, Any]] = []
    encode_calls: list[dict[str, Any]] = []
    encode_error: BaseException | None = None
    init_error: BaseException | None = None
    dim: int = _DIM

    @classmethod
    def reset(cls, *, dim: int = _DIM) -> None:
        cls.constructions = []
        cls.encode_calls = []
        cls.encode_error = None
        cls.init_error = None
        cls.dim = dim

    def __init__(self, model_name: str, device: str | None = None, **kwargs: Any) -> None:
        if type(self).init_error is not None:
            raise type(self).init_error
        self.model_name = model_name
        self.device = device
        type(self).constructions.append({"model_name": model_name, "device": device})

    def encode(self, sentences: Sequence[str], **kwargs: Any) -> FakeArray:
        type(self).encode_calls.append(
            {"sentences": list(sentences), "thread_id": threading.get_ident(), **kwargs}
        )
        if type(self).encode_error is not None:
            raise type(self).encode_error
        # Row i marks its input position in its first value -> order checks.
        return FakeArray(
            [[float(i)] + [0.0] * (type(self).dim - 1) for i in range(len(sentences))]
        )


def _install_fake_ml_stack(
    monkeypatch: pytest.MonkeyPatch,
    *,
    cuda_available: bool = False,
    sentence_transformers_module: types.ModuleType | None = None,
) -> None:
    fake_torch = types.ModuleType("torch")
    fake_torch.cuda = SimpleNamespace(  # type: ignore[attr-defined]
        is_available=lambda: cuda_available,
        OutOfMemoryError=FakeOutOfMemoryError,
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    if sentence_transformers_module is None:
        fake_st = types.ModuleType("sentence_transformers")
        fake_st.SentenceTransformer = FakeSentenceTransformer  # type: ignore[attr-defined]
    else:
        fake_st = sentence_transformers_module
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_st)


@pytest.fixture()
def fake_ml(monkeypatch: pytest.MonkeyPatch) -> type[FakeSentenceTransformer]:
    """Deterministic fake ML stack + isolated embedding settings."""
    _install_fake_ml_stack(monkeypatch)
    FakeSentenceTransformer.reset()
    monkeypatch.setattr(settings, "ai_embedding_model", _MODEL)
    monkeypatch.setattr(settings, "ai_embedding_dimension", _DIM)
    monkeypatch.setattr(settings, "ai_embedding_device", "auto")
    return FakeSentenceTransformer


# ---------------------------------------------------------------------------
# Construction / configuration
# ---------------------------------------------------------------------------


def test_provider_construction_does_not_load_model(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()

    assert provider.provider_name == "bge-m3"
    assert provider.dimension == _DIM
    assert FakeSentenceTransformer.constructions == []


def test_invalid_device_setting_raises_configuration_error(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    with pytest.raises(ConfigurationError, match="ai_embedding_device"):
        BGEM3EmbeddingProvider(device="tpu")


def test_invalid_dimension_raises_configuration_error(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    with pytest.raises(ConfigurationError, match="dimension must be >= 1"):
        BGEM3EmbeddingProvider(dimension=0)


# ---------------------------------------------------------------------------
# Device behavior (auto / cpu / cuda) — no real CUDA hardware needed
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auto_device_selects_cpu_without_cuda(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider(device="auto")

    result = await provider.embed("hello")

    assert FakeSentenceTransformer.constructions[0]["device"] == "cpu"
    assert result.metadata["device"] == "cpu"


@pytest.mark.asyncio
async def test_auto_device_selects_cuda_when_available(
    fake_ml: type[FakeSentenceTransformer],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_ml_stack(monkeypatch, cuda_available=True)
    provider = BGEM3EmbeddingProvider(device="auto")

    await provider.embed("hello")

    assert FakeSentenceTransformer.constructions[0]["device"] == "cuda"


@pytest.mark.asyncio
async def test_cpu_device_forces_cpu_even_when_cuda_available(
    fake_ml: type[FakeSentenceTransformer],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_ml_stack(monkeypatch, cuda_available=True)
    provider = BGEM3EmbeddingProvider(device="cpu")

    await provider.embed("hello")

    assert FakeSentenceTransformer.constructions[0]["device"] == "cpu"


@pytest.mark.asyncio
async def test_cuda_device_without_cuda_raises_provider_unavailable(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider(device="cuda")

    with pytest.raises(ProviderUnavailableError, match="no CUDA device"):
        await provider.embed("hello")

    assert FakeSentenceTransformer.constructions == []  # never constructed


# ---------------------------------------------------------------------------
# Lazy loading lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_model_loads_once_on_first_embed_and_is_reused(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()

    await provider.embed("first")
    await provider.embed("second")

    assert len(FakeSentenceTransformer.constructions) == 1
    assert FakeSentenceTransformer.constructions[0]["model_name"] == _MODEL
    assert len(FakeSentenceTransformer.encode_calls) == 2


# ---------------------------------------------------------------------------
# Single embedding
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embed_returns_dense_vector_with_configured_dimension(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()

    result = await provider.embed("مرحبا بالعالم")

    assert isinstance(result, EmbeddingResult)
    assert result.dimension == _DIM
    assert len(result.vector) == _DIM
    assert result.model == _MODEL
    assert result.provider == "bge-m3"
    assert result.metadata["normalized"] is True


@pytest.mark.asyncio
async def test_encode_is_called_with_conservative_batch_size_and_normalization(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()

    await provider.embed("hello")

    call = FakeSentenceTransformer.encode_calls[0]
    assert call["sentences"] == ["hello"]
    assert call["batch_size"] == 16
    assert call["normalize_embeddings"] is True
    assert call["show_progress_bar"] is False


# ---------------------------------------------------------------------------
# Batch embedding
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_embed_batch_preserves_count_and_order(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()
    texts = ["الأول", "second text", "third text"]

    results = await provider.embed_batch(texts)

    assert len(results) == 3
    # First vector component marks the input position (see fake encode).
    assert [r.vector[0] for r in results] == [0.0, 1.0, 2.0]
    assert all(len(r.vector) == _DIM for r in results)
    assert all(r.provider == "bge-m3" for r in results)
    assert FakeSentenceTransformer.encode_calls[0]["sentences"] == texts


@pytest.mark.asyncio
async def test_embed_batch_does_not_mutate_input(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()
    texts = ["a", "b"]

    await provider.embed_batch(texts)

    assert texts == ["a", "b"]


@pytest.mark.asyncio
async def test_empty_batch_returns_empty_without_loading_model(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()

    assert await provider.embed_batch([]) == []
    assert FakeSentenceTransformer.constructions == []


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_blank_text_raises_invalid_input_without_loading_model(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()

    with pytest.raises(InvalidInputError):
        await provider.embed("   ")

    assert FakeSentenceTransformer.constructions == []


@pytest.mark.asyncio
async def test_batch_containing_blank_text_raises_invalid_input(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()

    with pytest.raises(InvalidInputError):
        await provider.embed_batch(["ok", "  "])

    assert FakeSentenceTransformer.constructions == []  # validated before load


# ---------------------------------------------------------------------------
# Error mapping (existing PAL hierarchy, no broad except)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_encode_oom_maps_to_provider_unavailable(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    FakeSentenceTransformer.encode_error = FakeOutOfMemoryError("CUDA out of memory")
    provider = BGEM3EmbeddingProvider()

    with pytest.raises(ProviderUnavailableError, match="out of memory"):
        await provider.embed("hello")


@pytest.mark.asyncio
async def test_hub_timeout_during_load_maps_to_provider_timeout(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    FakeSentenceTransformer.init_error = requests.exceptions.Timeout(
        "hub read timed out"
    )
    provider = BGEM3EmbeddingProvider()

    with pytest.raises(ProviderTimeoutError, match="timed out"):
        await provider.embed("hello")


@pytest.mark.asyncio
async def test_hub_connection_error_during_load_maps_to_provider_unavailable(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    FakeSentenceTransformer.init_error = requests.exceptions.ConnectionError(
        "connection refused"
    )
    provider = BGEM3EmbeddingProvider()

    with pytest.raises(ProviderUnavailableError, match="Could not reach the model hub"):
        await provider.embed("hello")


@pytest.mark.asyncio
async def test_missing_sentence_transformers_maps_to_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_torch = types.ModuleType("torch")
    fake_torch.cuda = SimpleNamespace(  # type: ignore[attr-defined]
        is_available=lambda: False,
        OutOfMemoryError=FakeOutOfMemoryError,
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)  # -> ImportError
    monkeypatch.setattr(settings, "ai_embedding_model", _MODEL)
    monkeypatch.setattr(settings, "ai_embedding_dimension", _DIM)

    provider = BGEM3EmbeddingProvider()  # construction must still succeed

    with pytest.raises(ConfigurationError, match="not installed"):
        await provider.embed("hello")


@pytest.mark.asyncio
async def test_dimension_mismatch_maps_to_provider_server_error(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    FakeSentenceTransformer.reset(dim=768)  # model outputs 768 vs configured 1024
    provider = BGEM3EmbeddingProvider()

    with pytest.raises(ProviderServerError, match="shape"):
        await provider.embed("hello")


@pytest.mark.asyncio
async def test_unexpected_encode_error_propagates_unwrapped(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    FakeSentenceTransformer.encode_error = TypeError("unexpected inference bug")
    provider = BGEM3EmbeddingProvider()

    with pytest.raises(TypeError, match="unexpected inference bug"):
        await provider.embed("hello")


# ---------------------------------------------------------------------------
# Async boundary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_blocking_encode_runs_off_the_event_loop_thread(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider()

    await provider.embed("hello")

    call = FakeSentenceTransformer.encode_calls[0]
    assert call["thread_id"] != threading.get_ident()


# ---------------------------------------------------------------------------
# Health check and factory
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check_reports_configuration_without_loading_model(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = BGEM3EmbeddingProvider(device="cpu")

    status = await provider.health_check()

    assert status.healthy is True
    assert status.provider == "bge-m3"
    assert _MODEL in (status.message or "")
    assert FakeSentenceTransformer.constructions == []


def test_factory_maps_bge_m3_to_bge_m3_provider(
    fake_ml: type[FakeSentenceTransformer],
) -> None:
    provider = get_embedding_provider("bge-m3")

    assert isinstance(provider, BGEM3EmbeddingProvider)
    assert provider.dimension == _DIM
