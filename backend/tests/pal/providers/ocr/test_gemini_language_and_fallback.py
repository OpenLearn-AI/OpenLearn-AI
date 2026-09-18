"""Week 6 OCR-closure tests: language paths, interface contract, fallback.

Closes the remaining deterministic OCR test gaps using the existing Gemini
provider, the real PALRouter, and the existing MockOCRProvider — no
production changes.

* All Gemini interaction is faked (no network, no API key); the REAL
  ``google.genai.errors`` classes are used and constructed correctly for the
  installed SDK (``response_json`` must be a dict).
* Arabic/English coverage here proves the implementation *path*: the exact
  document bytes reach the SDK unmangled and the normalized OCRResult /
  router fallback behave language-agnostically. Real-corpus quality evidence
  is tracked separately (evidence gap, see the closure report).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from google.genai import errors as genai_errors

from app.pal.exceptions import ConfigurationError
from app.pal.interfaces.ocr import OCRInterface
from app.pal.models.types import HealthStatus, OCRResult
from app.pal.providers.ocr import gemini_provider
from app.pal.providers.ocr.gemini_provider import GeminiOCRProvider
from app.pal.providers.ocr.mock_provider import MockOCRProvider
from app.pal.router import PALRouter

_ARABIC_MARKER = "النص العربي التجريبي"
_ARABIC_TEXT = "هذا نص عربي تجريبي لاختبار مسار OCR"
_ENGLISH_MARKER = "english extraction marker"
_ENGLISH_TEXT = "This is English sample text for the OCR path."


# ---------------------------------------------------------------------------
# Deterministic single-page PDF fixture (byte-level only: the provider checks
# the %PDF header and forwards raw bytes; nothing here renders the page, so
# the embedded marker needs no font support).
# ---------------------------------------------------------------------------


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _single_page_pdf(marker: str) -> bytes:
    stream = f"BT /F1 24 Tf 72 700 Td ({_escape_pdf_text(marker)}) Tj ET".encode("utf-8")
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: (
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            "/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ).encode(),
        4: b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        5: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for num in sorted(objects):
        offsets[num] = len(out)
        out += f"{num} 0 obj\n".encode() + objects[num] + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 6\n0000000000 65535 f \n"
    for num in sorted(objects):
        out += f"{offsets[num]:010d} 00000 n \n".encode()
    out += b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
    out += f"startxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


def _write_pdf(tmp_path: Path, name: str, marker: str) -> tuple[Path, bytes]:
    pdf_bytes = _single_page_pdf(marker)
    path = tmp_path / name
    path.write_bytes(pdf_bytes)
    return path, pdf_bytes


# ---------------------------------------------------------------------------
# Fake google.genai plumbing (same proven pattern as the P7.2-B tests)
# ---------------------------------------------------------------------------


class FakeResponse:
    def __init__(self, text: str, finish_reason: str = "STOP") -> None:
        self.text = text
        self.candidates = [
            SimpleNamespace(finish_reason=SimpleNamespace(name=finish_reason))
        ]


def _install_fake_sdk(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: list[Any],
) -> dict[str, Any]:
    captured: dict[str, Any] = {"calls": []}
    state = {"index": 0}

    class _FakeModels:
        def generate_content(self, *, model: str, contents: list[Any], **kwargs: Any):
            index = state["index"]
            state["index"] = index + 1
            outcome = outcomes[index] if index < len(outcomes) else outcomes[-1]
            captured["calls"].append({"model": model, "contents": contents})
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

    class _FakeClient:
        def __init__(self, *, api_key: str | None = None, **kwargs: Any) -> None:
            self.models = _FakeModels()

    class _FakeGenai:
        Client = _FakeClient

    monkeypatch.setattr(gemini_provider, "genai", _FakeGenai)
    return captured


def _provider(
    monkeypatch: pytest.MonkeyPatch, outcomes: list[Any]
) -> tuple[GeminiOCRProvider, dict[str, Any]]:
    captured = _install_fake_sdk(monkeypatch, outcomes)
    return GeminiOCRProvider(api_key="test-key"), captured


# ---------------------------------------------------------------------------
# Interface contract
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_gemini_provider_satisfies_ocr_interface_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider, captured = _provider(monkeypatch, [FakeResponse(_ENGLISH_TEXT)])

    assert isinstance(provider, OCRInterface)
    assert provider.provider_name == "gemini"
    for operation in ("extract_text", "extract_text_batch", "health_check"):
        assert callable(getattr(provider, operation))

    status = await provider.health_check()
    assert isinstance(status, HealthStatus)
    assert status.healthy is True
    assert status.provider == "gemini"
    assert captured["calls"] == []  # health check performs no OCR request


# ---------------------------------------------------------------------------
# Arabic / English implementation paths
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_arabic_document_bytes_reach_gemini_and_arabic_text_is_normalized(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf, pdf_bytes = _write_pdf(tmp_path, "arabic-page.pdf", _ARABIC_MARKER)
    provider, captured = _provider(monkeypatch, [FakeResponse(_ARABIC_TEXT)])

    result = await provider.extract_text(str(pdf))

    assert isinstance(result, OCRResult)
    assert result.text == _ARABIC_TEXT  # Arabic survives normalization exactly
    assert result.provider == "gemini"
    assert result.regions == []  # no regions invented

    sent_part = captured["calls"][0]["contents"][0]
    assert sent_part.inline_data.mime_type == "application/pdf"
    assert sent_part.inline_data.data == pdf_bytes  # Arabic bytes unmangled

    prompt = captured["calls"][0]["contents"][1]
    assert isinstance(prompt, str)
    # The prompt is language-agnostic: it instructs extraction/preservation
    # without any language-specific wording.
    assert "extract the text" in prompt.lower()
    assert "preserve the original wording" in prompt.lower()


@pytest.mark.asyncio
async def test_english_document_bytes_reach_gemini_and_english_text_is_normalized(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf, pdf_bytes = _write_pdf(tmp_path, "english-page.pdf", _ENGLISH_MARKER)
    provider, captured = _provider(monkeypatch, [FakeResponse(_ENGLISH_TEXT)])

    result = await provider.extract_text(str(pdf))

    assert result.text == _ENGLISH_TEXT
    assert result.provider == "gemini"
    sent_part = captured["calls"][0]["contents"][0]
    assert sent_part.inline_data.mime_type == "application/pdf"
    assert sent_part.inline_data.data == pdf_bytes


@pytest.mark.asyncio
async def test_batch_preserves_order_across_arabic_and_english_documents(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    arabic_pdf, arabic_bytes = _write_pdf(tmp_path, "arabic.pdf", _ARABIC_MARKER)
    english_pdf, english_bytes = _write_pdf(tmp_path, "english.pdf", _ENGLISH_MARKER)
    provider, captured = _provider(
        monkeypatch,
        [FakeResponse(_ARABIC_TEXT), FakeResponse(_ENGLISH_TEXT)],
    )

    results = await provider.extract_text_batch([str(arabic_pdf), str(english_pdf)])

    assert [r.text for r in results] == [_ARABIC_TEXT, _ENGLISH_TEXT]
    assert all(r.provider == "gemini" for r in results)
    assert [call["contents"][0].inline_data.data for call in captured["calls"]] == [
        arabic_bytes,
        english_bytes,
    ]


# ---------------------------------------------------------------------------
# Fallback composition: real Gemini provider x real PALRouter x Mock
# ---------------------------------------------------------------------------


class CountingMockOCRProvider(MockOCRProvider):
    """MockOCRProvider that records how often it was invoked."""

    def __init__(self) -> None:
        self.calls = 0

    async def extract_text(self, source: str) -> OCRResult:
        self.calls += 1
        return await super().extract_text(source)


@pytest.mark.asyncio
async def test_gemini_rate_limit_falls_back_to_mock_via_pal_router(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf, _ = _write_pdf(tmp_path, "rate-limited.pdf", _ENGLISH_MARKER)
    provider, captured = _provider(
        monkeypatch,
        [genai_errors.ClientError(429, {}, "Resource exhausted")],
    )
    fallback = CountingMockOCRProvider()
    router = PALRouter([provider, fallback])

    result = await router.execute("extract_text", str(pdf))

    assert result.provider == "mock"  # fallback answered
    assert "Mock OCR result" in result.text
    assert len(captured["calls"]) == 1  # Gemini attempted exactly once
    assert fallback.calls == 1


@pytest.mark.asyncio
async def test_gemini_auth_error_does_not_trigger_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    pdf, _ = _write_pdf(tmp_path, "unauthorized.pdf", _ENGLISH_MARKER)
    provider, captured = _provider(
        monkeypatch,
        [genai_errors.ClientError(401, {}, "API key not valid")],
    )
    fallback = CountingMockOCRProvider()
    router = PALRouter([provider, fallback])

    with pytest.raises(ConfigurationError, match="authentication/permission"):
        await router.execute("extract_text", str(pdf))

    assert fallback.calls == 0  # configuration errors never fall back
    assert len(captured["calls"]) == 1
