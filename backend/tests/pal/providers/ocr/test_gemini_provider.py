"""P7.2-B tests: Gemini OCR provider against the frozen PAL OCR contract.

No real Gemini API calls: the ``google.genai`` module namespace used by the
provider is replaced with a deterministic fake, while the REAL
``google.genai.errors`` exception classes and REAL ``google.genai.types``
request models are used, so error mapping and request shape are genuinely
verified. Timeout/network failures are raised as the REAL ``requests``
transport exceptions (google-genai 1.24.0 has no ``errors.TimeoutError``).
No network, no credentials.
"""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import requests
from google.genai import errors as genai_errors
from google.genai import types

from app.config import settings
from app.pal.exceptions import (
    ConfigurationError,
    InvalidInputError,
    ProviderRateLimitError,
    ProviderServerError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.pal.factory import get_ocr_provider
from app.pal.models.types import OCRResult
from app.pal.providers.ocr import gemini_provider
from app.pal.providers.ocr.gemini_provider import GeminiOCRProvider

_MINIMAL_PDF_BYTES = b"%PDF-1.4\nminimal deterministic fixture page\n%%EOF\n"


# ---------------------------------------------------------------------------
# Real SDK exception builders (google-genai 1.24.0 requires response_json dict)
# ---------------------------------------------------------------------------


def _client_error(code: int, message: str) -> genai_errors.ClientError:
    """Build a REAL google-genai ClientError the way 1.24.0 requires.

    ``response_json`` must be a dict — the installed SDK dereferences it
    unconditionally, so ``None`` raises AttributeError inside the SDK (the
    original test bug). ``{}`` mirrors the payload the SDK itself builds via
    ``APIError.from_response`` for error responses without a JSON body.
    ClientError additionally enforces 400 <= code < 500.
    """
    return genai_errors.ClientError(code, {}, message)


def _server_error(code: int, message: str) -> genai_errors.ServerError:
    """Build a REAL google-genai ServerError (SDK enforces 500 <= code < 600)."""
    return genai_errors.ServerError(code, {}, message)


# ---------------------------------------------------------------------------
# Fake google-genai plumbing
# ---------------------------------------------------------------------------


class FakeResponse:
    """Minimal stand-in for ``types.GenerateContentResponse``."""

    def __init__(
        self,
        text: str | None = "Hello world",
        finish_reason: str | None = "STOP",
    ) -> None:
        self.text = text
        if finish_reason is None:
            self.candidates: list[Any] = []
        else:
            self.candidates = [
                SimpleNamespace(finish_reason=SimpleNamespace(name=finish_reason))
            ]


def _install_fake_sdk(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: list[Any],
) -> dict[str, Any]:
    """Replace ``gemini_provider.genai`` with a deterministic fake.

    ``outcomes`` is consumed one entry per ``generate_content`` call (the
    last entry repeats). Entries are returned as-is, or raised when they are
    exception instances (real SDK or real requests exceptions). Returns a
    capture dict for assertions.
    """
    captured: dict[str, Any] = {"calls": [], "thread_ids": [], "api_keys": []}
    state = {"index": 0}

    class _FakeModels:
        def generate_content(self, *, model: str, contents: list[Any], **kwargs: Any):
            index = state["index"]
            state["index"] = index + 1
            outcome = outcomes[index] if index < len(outcomes) else outcomes[-1]
            captured["calls"].append({"model": model, "contents": contents})
            captured["thread_ids"].append(threading.get_ident())
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

    class _FakeClient:
        def __init__(self, *, api_key: str | None = None, **kwargs: Any) -> None:
            captured["api_keys"].append(api_key)
            self.models = _FakeModels()

    class _FakeGenai:
        Client = _FakeClient

    monkeypatch.setattr(gemini_provider, "genai", _FakeGenai)
    return captured


def _configured_provider(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: list[Any],
) -> tuple[GeminiOCRProvider, dict[str, Any]]:
    monkeypatch.setattr(settings, "gemini_api_key", "test-api-key")
    monkeypatch.setattr(settings, "ai_ocr_model", "gemini-2.5-flash")
    captured = _install_fake_sdk(monkeypatch, outcomes)
    return GeminiOCRProvider(), captured


def _pdf_file(tmp_path: Path, name: str, content: bytes = _MINIMAL_PDF_BYTES) -> Path:
    path = tmp_path / name
    path.write_bytes(content)
    return path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def test_missing_api_key_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "gemini_api_key", "")
    with pytest.raises(ConfigurationError, match="API key"):
        GeminiOCRProvider()


@pytest.mark.asyncio
async def test_configured_provider_initializes_and_health_check_is_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _install_fake_sdk(monkeypatch, [FakeResponse()])
    monkeypatch.setattr(settings, "gemini_api_key", "test-api-key")

    provider = GeminiOCRProvider()

    assert provider.provider_name == "gemini"
    assert captured["api_keys"] == ["test-api-key"]  # client built with key

    health = await provider.health_check()  # readiness only — no OCR call
    assert health.healthy is True
    assert health.provider == "gemini"
    assert captured["calls"] == []  # health check made no API request


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_extract_text_missing_source_raises_invalid_input(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, captured = _configured_provider(monkeypatch, [FakeResponse()])

    with pytest.raises(InvalidInputError, match="does not exist"):
        await provider.extract_text(str(tmp_path / "ghost.pdf"))

    assert captured["calls"] == []  # no SDK call on invalid input


@pytest.mark.asyncio
async def test_extract_text_directory_source_raises_invalid_input(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, captured = _configured_provider(monkeypatch, [FakeResponse()])

    with pytest.raises(InvalidInputError, match="not a file"):
        await provider.extract_text(str(tmp_path))

    assert captured["calls"] == []


@pytest.mark.asyncio
async def test_extract_text_non_pdf_source_raises_invalid_input(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, _ = _configured_provider(monkeypatch, [FakeResponse()])
    notes = tmp_path / "notes.txt"
    notes.write_text("just text", encoding="utf-8")

    with pytest.raises(InvalidInputError, match="requires a PDF"):
        await provider.extract_text(str(notes))


@pytest.mark.asyncio
async def test_extract_text_mislabeled_pdf_raises_invalid_input(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, _ = _configured_provider(monkeypatch, [FakeResponse()])
    fake = _pdf_file(tmp_path, "fake.pdf", content=b"definitely not a pdf")

    with pytest.raises(InvalidInputError, match="not a valid PDF"):
        await provider.extract_text(str(fake))


# ---------------------------------------------------------------------------
# Successful OCR
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_extract_text_builds_gemini_request_and_normalizes_result(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, captured = _configured_provider(
        monkeypatch, [FakeResponse(text="Hello world")]
    )
    pdf = _pdf_file(tmp_path, "page.pdf")

    result = await provider.extract_text(str(pdf))

    assert isinstance(result, OCRResult)
    assert result.text == "Hello world"
    assert result.provider == "gemini"
    assert result.regions == []  # no regions invented

    call = captured["calls"][0]
    assert call["model"] == "gemini-2.5-flash"  # configured default model

    expected_part = types.Part.from_bytes(
        data=_MINIMAL_PDF_BYTES, mime_type="application/pdf"
    )
    assert call["contents"][0] == expected_part
    assert call["contents"][0].inline_data.mime_type == "application/pdf"
    assert call["contents"][0].inline_data.data == _MINIMAL_PDF_BYTES

    prompt = call["contents"][1]
    assert isinstance(prompt, str)
    assert "extract the text" in prompt.lower()
    assert "preserve the original wording" in prompt.lower()
    assert "do not summarize" in prompt.lower()
    assert "return only the extracted text" in prompt.lower()

    assert result.metadata["model"] == "gemini-2.5-flash"
    assert result.metadata["finish_reason"] == "STOP"


@pytest.mark.asyncio
async def test_extract_text_honors_explicit_model_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, captured = _configured_provider(
        monkeypatch, [FakeResponse(text="ok"), FakeResponse(text="ok")]
    )
    pdf = _pdf_file(tmp_path, "page.pdf")

    override = GeminiOCRProvider(model="gemini-2.5-pro")
    await provider.extract_text(str(pdf))
    await override.extract_text(str(pdf))

    assert captured["calls"][0]["model"] == "gemini-2.5-flash"
    assert captured["calls"][1]["model"] == "gemini-2.5-pro"


# ---------------------------------------------------------------------------
# Error mapping (real google.genai.errors classes, correctly constructed)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rate_limit_maps_to_provider_rate_limit_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sdk_error = _client_error(429, "Resource exhausted")
    provider, _ = _configured_provider(monkeypatch, [sdk_error])
    pdf = _pdf_file(tmp_path, "page.pdf")

    with pytest.raises(ProviderRateLimitError, match="429") as excinfo:
        await provider.extract_text(str(pdf))

    assert excinfo.value.__cause__ is sdk_error  # chained


@pytest.mark.asyncio
@pytest.mark.parametrize("code", [401, 403])
async def test_auth_failure_maps_to_configuration_error_not_rate_limit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, code: int
) -> None:
    sdk_error = _client_error(code, "API key not valid")
    provider, _ = _configured_provider(monkeypatch, [sdk_error])
    pdf = _pdf_file(tmp_path, "page.pdf")

    with pytest.raises(ConfigurationError, match="authentication/permission") as excinfo:
        await provider.extract_text(str(pdf))

    assert f"HTTP {code}" in str(excinfo.value)
    assert excinfo.value.__cause__ is sdk_error
    assert not isinstance(excinfo.value, ProviderRateLimitError)


@pytest.mark.asyncio
async def test_server_error_maps_to_provider_server_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sdk_error = _server_error(500, "Internal error")
    provider, _ = _configured_provider(monkeypatch, [sdk_error])
    pdf = _pdf_file(tmp_path, "page.pdf")

    with pytest.raises(ProviderServerError, match="500") as excinfo:
        await provider.extract_text(str(pdf))

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_transport_timeout_maps_to_provider_timeout_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # google-genai 1.24.0 has no errors.TimeoutError: the sync client is
    # requests-based, so real timeouts surface as requests exceptions.
    sdk_error = requests.exceptions.ReadTimeout("Read timed out after 60000 ms")
    provider, _ = _configured_provider(monkeypatch, [sdk_error])
    pdf = _pdf_file(tmp_path, "page.pdf")

    with pytest.raises(ProviderTimeoutError, match="timed out") as excinfo:
        await provider.extract_text(str(pdf))

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_connection_error_maps_to_provider_unavailable_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    sdk_error = requests.exceptions.ConnectionError("Connection refused")
    provider, _ = _configured_provider(monkeypatch, [sdk_error])
    pdf = _pdf_file(tmp_path, "page.pdf")

    with pytest.raises(ProviderUnavailableError, match="connection failed") as excinfo:
        await provider.extract_text(str(pdf))

    assert excinfo.value.__cause__ is sdk_error


@pytest.mark.asyncio
async def test_unexpected_exception_propagates_unwrapped(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Guards against a broad "except Exception" fallback in the provider.
    provider, _ = _configured_provider(monkeypatch, [TypeError("unexpected")])
    pdf = _pdf_file(tmp_path, "page.pdf")

    with pytest.raises(TypeError, match="unexpected"):
        await provider.extract_text(str(pdf))


@pytest.mark.asyncio
async def test_missing_text_content_raises_provider_server_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, _ = _configured_provider(monkeypatch, [FakeResponse(text=None)])
    pdf = _pdf_file(tmp_path, "page.pdf")

    with pytest.raises(ProviderServerError, match="no text content"):
        await provider.extract_text(str(pdf))


# ---------------------------------------------------------------------------
# Batch and async boundary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_extract_text_batch_preserves_order(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, captured = _configured_provider(
        monkeypatch,
        [FakeResponse(text="first page text"), FakeResponse(text="second page text")],
    )
    page1 = _pdf_file(tmp_path, "page1.pdf")
    page2 = _pdf_file(tmp_path, "page2.pdf")

    results = await provider.extract_text_batch([str(page1), str(page2)])

    assert [r.text for r in results] == ["first page text", "second page text"]
    assert all(r.provider == "gemini" for r in results)
    assert len(captured["calls"]) == 2


@pytest.mark.asyncio
async def test_extract_text_offloads_blocking_sdk_call_to_thread(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider, captured = _configured_provider(
        monkeypatch, [FakeResponse(text="threaded")]
    )
    pdf = _pdf_file(tmp_path, "page.pdf")

    real_to_thread = asyncio.to_thread
    delegated: list[tuple[Any, tuple[Any, ...]]] = []

    async def spy_to_thread(func: Any, /, *args: Any, **kwargs: Any) -> Any:
        delegated.append((func, args))
        return await real_to_thread(func, *args, **kwargs)

    monkeypatch.setattr(gemini_provider.asyncio, "to_thread", spy_to_thread)

    result = await provider.extract_text(str(pdf))

    assert result.text == "threaded"
    assert len(delegated) == 1
    func, args = delegated[0]
    assert func.__name__ == "_generate"          # the blocking SDK wrapper
    assert args == (_MINIMAL_PDF_BYTES,)
    # The blocking call ran on a worker thread, not on the event loop thread.
    assert captured["thread_ids"][0] != threading.get_ident()


# ---------------------------------------------------------------------------
# Factory integration
# ---------------------------------------------------------------------------


def test_factory_maps_gemini_to_gemini_ocr_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "gemini_api_key", "test-api-key")
    _install_fake_sdk(monkeypatch, [FakeResponse()])

    provider = get_ocr_provider("gemini")

    assert isinstance(provider, GeminiOCRProvider)
