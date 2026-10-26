"""BGE-M3 local embedding provider (P9-A).

Implements the frozen PAL ``EmbeddingInterface`` contract using
``sentence-transformers`` with ``BAAI/bge-m3``. Dense embeddings only —
sparse/ColBERT outputs, reranking, retrieval and vector storage are out of
scope for P9.

Responsibility (PAL provider boundary per ADR-0009):

    text(s) -> lazily loaded local SentenceTransformer -> EmbeddingResult(s)

Design points:

* Lazy loading: the module import, the application import, and provider
  construction never load the model. The first embed/embed_batch call loads
  ``SentenceTransformer`` once and caches it behind a ``threading.Lock``
  (inference runs on worker threads via ``asyncio.to_thread``).
* Device: ``settings.ai_embedding_device`` is one of ``auto`` (CUDA when
  ``torch.cuda.is_available()``, else CPU), ``cpu`` (forced) or ``cuda``
  (requires CUDA, otherwise ProviderUnavailableError). CPU inference is
  always sufficient — the AWS staging host has no CUDA GPU.
* Async boundary: ``SentenceTransformer.encode`` is blocking and never runs
  on the event loop thread.
* Embeddings are L2-normalized (BGE retrieval recipe), so downstream cosine
  similarity reduces to a dot product.
* Conservative internal encode batch size (16) for predictable memory on
  the 2 vCPU / 8 GiB staging host; deliberately not configurable (P9-A).
* ``torch``/``sentence_transformers`` are imported lazily inside the load
  path, keeping application import cheap. Failures are mapped onto the
  existing PAL hierarchy — no new exceptions, no broad ``except Exception``.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

import requests

from app.config import settings
from app.pal.exceptions import (
    ConfigurationError,
    InvalidInputError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.pal.interfaces.embedding import EmbeddingInterface
from app.pal.models.types import EmbeddingResult, HealthStatus

if TYPE_CHECKING:  # type-hints only; the real import happens lazily on load
    from sentence_transformers import SentenceTransformer

#: Accepted values for ``settings.ai_embedding_device``.
_VALID_DEVICES = ("auto", "cpu", "cuda")

#: Conservative encode batch size: predictable memory on the 2 vCPU /
#: 8 GiB AWS staging host. Deliberately NOT configurable in P9-A.
_ENCODE_BATCH_SIZE = 16


class BGEM3EmbeddingProvider(EmbeddingInterface):
    """Local dense embedding provider backed by BAAI/bge-m3."""

    provider_name = "bge-m3"

    def __init__(
        self,
        model_name: str | None = None,
        dimension: int | None = None,
        device: str | None = None,
    ) -> None:
        self._model_name = (
            model_name if model_name is not None else settings.ai_embedding_model
        )
        self._dimension = (
            dimension if dimension is not None else settings.ai_embedding_dimension
        )
        self._device_setting = (
            device if device is not None else settings.ai_embedding_device
        ).strip().lower()
        if self._device_setting not in _VALID_DEVICES:
            raise ConfigurationError(
                f"Invalid ai_embedding_device '{self._device_setting}'; "
                f"expected one of: {', '.join(_VALID_DEVICES)}."
            )
        if self._dimension < 1:
            raise ConfigurationError(
                f"Embedding dimension must be >= 1, got {self._dimension}."
            )
        # Model state: nothing is loaded until the first encode request.
        self._model: SentenceTransformer | None = None
        self._resolved_device: str | None = None
        self._lock = threading.Lock()

    @property
    def dimension(self) -> int:
        """Configured dense dimension (BGE-M3: 1024). The model stays lazy."""
        return self._dimension

    async def health_check(self) -> HealthStatus:
        """Configuration/readiness check — never loads the multi-GB model."""
        return HealthStatus(
            healthy=True,
            provider=self.provider_name,
            message=(
                f"BGE-M3 embedding provider is configured "
                f"(model: {self._model_name}, device: {self._device_setting})."
            ),
        )

    async def embed(self, text: str) -> EmbeddingResult:
        """Embed one text into a dense, L2-normalized vector."""
        self._validate_text(text)
        vectors = await asyncio.to_thread(self._encode_texts, [text])
        return EmbeddingResult(
            vector=vectors[0],
            dimension=self._dimension,
            model=self._model_name,
            provider=self.provider_name,
            metadata=self._encode_metadata(),
        )

    async def embed_batch(
        self,
        texts: Sequence[str],
    ) -> list[EmbeddingResult]:
        """Embed texts in input order via a single blocking encode call."""
        materialized = list(texts)  # defensive copy; never mutate caller input
        if not materialized:
            return []  # empty batch: no model load, nothing to encode
        for text in materialized:
            self._validate_text(text)
        vectors = await asyncio.to_thread(self._encode_texts, materialized)
        return [
            EmbeddingResult(
                vector=vector,
                dimension=self._dimension,
                model=self._model_name,
                provider=self.provider_name,
                metadata=self._encode_metadata(),
            )
            for vector in vectors
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_text(text: str) -> None:
        if not text.strip():
            raise InvalidInputError(
                "Embedding input must be a non-empty, non-blank string."
            )

    def _encode_metadata(self) -> dict[str, Any]:
        return {
            "device": self._resolved_device or self._device_setting,
            "normalized": True,
        }

    def _get_model(self) -> tuple["SentenceTransformer", str]:
        """Return the cached model, loading it once (thread-safe)."""
        with self._lock:
            if self._model is None:
                self._model, self._resolved_device = self._load_model()
            assert self._model is not None and self._resolved_device is not None
            return self._model, self._resolved_device

    def _load_model(self) -> tuple["SentenceTransformer", str]:
        try:
            import torch  # lazy: keeps application import light
            import sentence_transformers
        except ImportError as exc:
            raise ConfigurationError(
                "sentence-transformers/torch are not installed; the "
                "'bge-m3' embedding provider requires them."
            ) from exc

        device = self._resolve_device(torch)
        try:
            model = sentence_transformers.SentenceTransformer(
                self._model_name,
                device=device,
            )
        except requests.exceptions.Timeout as exc:
            raise ProviderTimeoutError(
                f"Timed out loading BGE-M3 model '{self._model_name}': {exc}"
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise ProviderUnavailableError(
                f"Could not reach the model hub to load "
                f"'{self._model_name}': {exc}"
            ) from exc
        except torch.cuda.OutOfMemoryError as exc:
            raise ProviderUnavailableError(
                f"Not enough memory to load BGE-M3 on device '{device}': {exc}"
            ) from exc
        return model, device

    def _resolve_device(self, torch_module: Any) -> str:
        """Map the ai_embedding_device setting to a concrete torch device."""
        if self._device_setting == "cpu":
            return "cpu"
        cuda_available = torch_module.cuda.is_available()
        if self._device_setting == "cuda":
            if not cuda_available:
                raise ProviderUnavailableError(
                    "ai_embedding_device='cuda' but no CUDA device is available; "
                    "use 'auto' or 'cpu' (CPU inference is fully supported)."
                )
            return "cuda"
        return "cuda" if cuda_available else "cpu"  # auto

    def _encode_texts(self, texts: list[str]) -> list[list[float]]:
        """Blocking encode — always executed via ``asyncio.to_thread``."""
        import torch  # lazy; also provides the OOM exception surface

        model, device = self._get_model()
        try:
            embeddings = model.encode(
                texts,
                batch_size=_ENCODE_BATCH_SIZE,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        except torch.cuda.OutOfMemoryError as exc:
            raise ProviderUnavailableError(
                f"BGE-M3 embedding ran out of memory on device '{device}': {exc}"
            ) from exc

        # Provider-side shape validation: a wrong-dimensional model output is
        # a provider failure, not caller input (pydantic backstops anyway).
        expected = (len(texts), self._dimension)
        if tuple(embeddings.shape) != expected:
            raise ProviderServerError(
                f"BGE-M3 returned embeddings with shape "
                f"{tuple(embeddings.shape)}, expected {expected}; check "
                f"ai_embedding_model / ai_embedding_dimension."
            )
        return [embeddings[i].tolist() for i in range(len(texts))]
