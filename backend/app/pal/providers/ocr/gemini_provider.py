"""Gemini OCR provider (P7.2-B).

Implements the frozen PAL ``OCRInterface`` contract using the official
``google-genai`` SDK. The provider is responsible ONLY for:

    local PDF path -> read bytes -> Gemini API request -> OCRResult

It knows nothing about CanonicalDocument/Page, OCR quality thresholds, page
iteration, PDF splitting/rendering, RAG, WebSocket, or fallback orchestration
— those live in the application service layer (services/ocr.py,
services/ocr_source.py per ADR-0009).

Exception surface (verified against the installed google-genai 1.24.0):

* ``google.genai.errors`` exposes exactly ``APIError`` (base, carries
  ``.code``), ``ClientError`` (HTTP 4xx) and ``ServerError`` (HTTP 5xx).
  There is NO ``errors.TimeoutError`` in this SDK version.
* The synchronous client (the only one used here, invoked via
  ``asyncio.to_thread``) is built on ``requests``, and the SDK does not wrap
  transport exceptions. Timeouts and connection failures therefore surface
  as ``requests.exceptions.Timeout`` / ``requests.exceptions.ConnectionError``
  and are handled explicitly — never via a broad ``except Exception``.

The synchronous SDK call is executed through ``asyncio.to_thread`` so the
FastAPI event loop is never blocked. Failures are mapped onto the existing
PAL exception hierarchy — no provider-specific exceptions are introduced.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

import requests

from app.config import settings
from app.pal.exceptions import (
    ConfigurationError,
    InvalidInputError,
    ProviderRateLimitError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.pal.interfaces.ocr import OCRInterface
from app.pal.models.types import HealthStatus, OCRResult

#: Instructions sent with every OCR request. Plain text only — no JSON, no
#: structured output. Gemini must return just the extracted text.
_OCR_PROMPT = (
    "Extract the text from the supplied PDF page. "
    "Preserve the original wording exactly. "
    "Preserve the natural reading order, paragraphs, and headings where "
    "possible. Do not summarize. Do not explain the document. "
    "Return only the extracted text."
)

#: HTTP statuses treated as authentication/permission failures. These are
#: configuration problems, NOT rate limits and NOT retryable outages.
_AUTH_STATUS_CODES = frozenset({401, 403})


class GeminiOCRProvider(OCRInterface):
    """OCR provider backed by the Google Gemini API (google-genai SDK)."""

    provider_name = "gemini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.gemini_api_key
        self._model = model if model is not None else settings.ai_ocr_model
        if not self._api_key:
            raise ConfigurationError(
                "Gemini OCR provider requires an API key (set GEMINI_API_KEY)."
            )
        # Local construction only — no network access happens here.
        self._client = genai.Client(api_key=self._api_key)

    async def health_check(self) -> HealthStatus:
        """Configuration/readiness check — never performs an OCR request."""
        return HealthStatus(
            healthy=True,
            provider=self.provider_name,
            message=f"Gemini OCR provider is configured (model: {self._model}).",
        )

    async def extract_text(self, source: str) -> OCRResult:
        """OCR one local single-page PDF via Gemini and normalize the result."""
        pdf_bytes = self._read_pdf_bytes(source)

        try:
            # Blocking SDK call off the event loop thread.
            response = await asyncio.to_thread(self._generate, pdf_bytes)
        except requests.exceptions.Timeout as exc:
            # Must precede ConnectionError: requests' ConnectTimeout inherits
            # from BOTH, and a timeout is the more specific diagnosis.
            raise ProviderTimeoutError(
                f"Gemini OCR request timed out: {exc}"
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise ProviderUnavailableError(
                f"Gemini OCR connection failed: {exc}"
            ) from exc
        except genai_errors.ClientError as exc:
            raise self._map_client_error(exc) from exc
        except genai_errors.ServerError as exc:
            raise ProviderServerError(
                f"Gemini OCR server error (HTTP {exc.code}): {exc}"
            ) from exc
        except genai_errors.APIError as exc:
            # Any other typed API error (non-4xx/5xx code) is a provider-side
            # failure; safe to retry via PAL fallback.
            raise ProviderServerError(
                f"Gemini OCR API error (HTTP {exc.code}): {exc}"
            ) from exc

        extracted_text = response.text
        if extracted_text is None:
            # No candidates / no text parts: provider-side anomaly. Never
            # silently return a non-answer; safe to retry via fallback.
            raise ProviderServerError(
                f"Gemini OCR returned no text content for source '{source}'."
            )

        return OCRResult(
            text=extracted_text,
            provider=self.provider_name,
            metadata=self._response_metadata(response),
        )

    async def extract_text_batch(
        self,
        sources: Sequence[str],
    ) -> list[OCRResult]:
        """Sequential batch OCR — one normalized result per input, order kept."""
        return [await self.extract_text(source) for source in sources]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate(self, pdf_bytes: bytes) -> types.GenerateContentResponse:
        """Blocking Gemini request — always run via ``asyncio.to_thread``."""
        contents = [
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            _OCR_PROMPT,
        ]
        return self._client.models.generate_content(
            model=self._model,
            contents=contents,
        )

    def _read_pdf_bytes(self, source: str) -> bytes:
        path = Path(source)
        if not path.exists():
            raise InvalidInputError(f"Gemini OCR source does not exist: {source}")
        if not path.is_file():
            raise InvalidInputError(f"Gemini OCR source is not a file: {source}")
        if path.suffix.lower() != ".pdf":
            raise InvalidInputError(
                f"Gemini OCR requires a PDF source; got extension "
                f"'{path.suffix or '<none>'}' for {source}"
            )
        pdf_bytes = path.read_bytes()
        if not pdf_bytes.startswith(b"%PDF-"):
            raise InvalidInputError(
                f"Gemini OCR source is not a valid PDF (bad header): {source}"
            )
        return pdf_bytes

    def _map_client_error(self, exc: genai_errors.ClientError) -> Exception:
        if exc.code == 429:
            return ProviderRateLimitError(
                f"Gemini OCR rate limited (HTTP 429): {exc}"
            )
        if exc.code in _AUTH_STATUS_CODES:
            return ConfigurationError(
                f"Gemini OCR authentication/permission error "
                f"(HTTP {exc.code}): {exc}"
            )
        return InvalidInputError(
            f"Gemini OCR rejected the request (HTTP {exc.code}): {exc}"
        )

    def _response_metadata(self, response: Any) -> dict[str, Any]:
        """Small, stable metadata only — the raw SDK response is never dumped."""
        metadata: dict[str, Any] = {"model": self._model}
        candidates = getattr(response, "candidates", None)
        if candidates:
            finish_reason = candidates[0].finish_reason
            if finish_reason is not None:
                metadata["finish_reason"] = getattr(
                    finish_reason, "name", str(finish_reason)
                )
        return metadata
